#!/bin/sh
set -e -u

# install curl and jq
apk add --no-cache curl jq 1> /dev/null

# Create user if not exists
USER=$(
  curl "${MLFLOW_URL}/api/2.0/mlflow/users/get?username=${USERNAME}" \
    --user "${ADMIN}" \
    --silent --show-error
)
USER_ID=$(echo "${USER}" | jq --raw-output '.user.id // empty')
if [ -z "${USER_ID}" ]; then
  echo "Creating user: ${USERNAME}"
  USER_ID=$(
    curl --request POST "${MLFLOW_URL}/api/2.0/mlflow/users/create" \
      --user "${ADMIN}" \
      --header "Content-Type: application/json" \
      --data "{\"username\": \"${USERNAME}\", \"password\": \"${PASSWORD}\"}" \
      --silent --show-error --fail |
      jq --raw-output '.user.id // empty'
  )
  if [ -z "${USER_ID}" ]; then
    echo "Unexpected user ID for '${USERNAME}', received null." 1>&2
    exit 1
  fi
  echo "User '${USERNAME}' created."
else
  echo "User '${USERNAME}' already exists, skipping."
fi

# Create workspace if not exists
WORKSPACE_EXISTS=$(
  curl "${MLFLOW_URL}/api/3.0/mlflow/workspaces" \
    --user "${ADMIN}" \
    --silent --show-error --fail |
    jq --raw-output --arg name "${WORKSPACE_NAME}" 'any(.workspaces[]; .name == $name)'
)
if [ "${WORKSPACE_EXISTS}" = "false" ]; then
  echo "Creating workspace: ${WORKSPACE_NAME}"
  ADDED_WORKSPACE_NAME=$(
    curl --request POST "${MLFLOW_URL}/api/3.0/mlflow/workspaces" \
      --user "${ADMIN}" \
      --header "Content-Type: application/json" \
      --data "{\"name\": \"${WORKSPACE_NAME}\"}" \
      --silent --show-error --fail |
      jq --raw-output '.workspace.name // empty'
  )
  if [ "${ADDED_WORKSPACE_NAME}" != "${WORKSPACE_NAME}" ]; then
    echo "Unexpected value '${ADDED_WORKSPACE_NAME}', expecting '${WORKSPACE_NAME}'." 1>&2
    exit 1
  fi
  echo "Workspace '${WORKSPACE_NAME}' created."
elif [ "${WORKSPACE_EXISTS}" = "true" ]; then
  echo "Workspace '${WORKSPACE_NAME}' already exists, skipping."
else
  echo "Unexpected value '${WORKSPACE_EXISTS}' expecting a boolean string." 1>&2
  exit 1
fi

# Create role if not exists
ROLE_ID=$(
  curl "${MLFLOW_URL}/api/3.0/mlflow/roles/list" \
    --user "${ADMIN}" \
    --silent --show-error --fail |
    jq --raw-output --arg name "${ROLE_NAME}" --arg workspace "${WORKSPACE_NAME}" \
      '.roles | map(select(.name == $name and .workspace == $workspace)) | if length > 0 then .[0].id else empty end'
)
if [ -z "${ROLE_ID}" ]; then
  echo "Creating role: ${ROLE_NAME}"
  ROLE_ID=$(
    curl --request POST "${MLFLOW_URL}/api/3.0/mlflow/roles/create" \
      --user "${ADMIN}" \
      --header "Content-Type: application/json" \
      --data "{\"name\": \"${ROLE_NAME}\", \"workspace\": \"${WORKSPACE_NAME}\"}" \
      --silent --show-error --fail |
      jq --raw-output '.role.id // empty'
  )
  if [ -z "${ROLE_ID}" ]; then
    echo "Unexpected role ID for '${ROLE_NAME}', received null." 1>&2
    exit 1
  fi
  echo "Role '${ROLE_NAME}' created."
else
  echo "Role '${ROLE_NAME}' already exists, skipping."
fi

# Add MANAGE permission to role if not set
ROLE_HAS_PERMISSION=$(
  curl "${MLFLOW_URL}/api/3.0/mlflow/roles/list" \
    --user "${ADMIN}" \
    --silent --show-error --fail |
    jq --raw-output --argjson id "${ROLE_ID}" \
      'any(.roles[] | select(.id == $id) | .permissions[]; .resource_type == "workspace" and .resource_pattern == "*" and .permission == "MANAGE")'
)
if [ "${ROLE_HAS_PERMISSION}" = "false" ]; then
  echo "Adding MANAGE permission for all resources in '${WORKSPACE_NAME}' workspace to role '${ROLE_NAME}'."
  ADDED_PERMISSION=$(
    curl --request POST "${MLFLOW_URL}/api/3.0/mlflow/roles/permissions/add" \
      --user "${ADMIN}" \
      --header "Content-Type: application/json" \
      --data "{\"role_id\": \"${ROLE_ID}\", \"resource_type\": \"workspace\", \"resource_pattern\": \"*\", \"permission\": \"MANAGE\"}" \
      --silent --show-error --fail |
      jq --raw-output '.role_permission.permission // empty'
  )
  if [ "${ADDED_PERMISSION}" != "MANAGE" ]; then
    echo "Unexpected permission '${ADDED_PERMISSION}', expecting 'MANAGE'." 1>&2
    exit 1
  fi
  echo "Permission added to '${ROLE_NAME}' role."
elif [ "${ROLE_HAS_PERMISSION}" = "true" ]; then
  echo "Role '${ROLE_NAME}' already has MANAGE permission for all resources in '${WORKSPACE_NAME}' workspace, skipping."
else
  echo "Unexpected value '${ROLE_HAS_PERMISSION}' expecting a boolean string." 1>&2
  exit 1
fi

# Assign role to user if not assigned
ROLE_ASSIGNED=$(
  curl "${MLFLOW_URL}/api/3.0/mlflow/users/roles/list?username=${USERNAME}" \
    --user "${ADMIN}" \
    --silent --show-error --fail |
    jq --raw-output --argjson id "${ROLE_ID}" 'any(.roles[]; .id == $id)'
)
if [ "${ROLE_ASSIGNED}" = "false" ]; then
  echo "Assigning '${ROLE_NAME}' role to user '${USERNAME}'."
  ASSIGNMENT_ID=$(
    curl --request POST "${MLFLOW_URL}/api/3.0/mlflow/roles/assign" \
      --user "${ADMIN}" \
      --header "Content-Type: application/json" \
      --data "{\"username\": \"${USERNAME}\", \"role_id\": \"${ROLE_ID}\", \"workspace\": \"${WORKSPACE_NAME}\"}" \
      --silent --show-error --fail |
      jq --raw-output '.assignment.id // empty'
  )
  if [ -z "${ASSIGNMENT_ID}" ]; then
    echo "Unexpected assignment ID for user '${USERNAME}', received null." 1>&2
    exit 1
  fi
  echo "'${ROLE_NAME}' role assigned to user '${USERNAME}'."
elif [ "${ROLE_ASSIGNED}" = "true" ]; then
  echo "User '${USERNAME}' already has '${ROLE_NAME}' role assigned, skipping."
else
  echo "Unexpected value '${ROLE_ASSIGNED}' expecting a boolean string." 1>&2
  exit 1
fi

# Verify user permission to workspace
IS_PERMITTED=$(
  curl "${MLFLOW_URL}/api/3.0/mlflow/users/permissions/list?username=${USERNAME}" \
    --user "${ADMIN}" \
    --silent --show-error --fail |
    jq --raw-output --arg workspace "${WORKSPACE_NAME}" \
      'any(.permissions[]; .workspace == $workspace and .resource_type == "workspace" and .resource_pattern == "*" and .permission == "MANAGE")'
)
if [ "${IS_PERMITTED}" != "true" ]; then
  echo "Verification failed: '${USERNAME}' user does not have MANAGE permission on workspace '${WORKSPACE_NAME}'." 1>&2
  exit 1
fi
echo "Verified: '${USERNAME}' user has MANAGE permission on workspace '${WORKSPACE_NAME}'."

echo "Done."