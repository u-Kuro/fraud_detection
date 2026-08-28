#!/bin/sh
set -e -u

# install curl and jq
apk add --no-cache curl jq 1> /dev/null

# Create user if not exists
USER_STATUS=$(
  curl "${MLFLOW_URL}/api/2.0/mlflow/users/get?username=${USERNAME}" \
    --user "${ADMIN}" \
    --write-out "%{http_code}" --output /dev/null \
    --silent --show-error
)

if [ "$USER_STATUS" != "200" ]; then
  echo "Creating user: ${USERNAME}"
  curl --request POST "${MLFLOW_URL}/api/2.0/mlflow/users/create" \
    --user "${ADMIN}" \
    --header "Content-Type: application/json" \
    --data "{\"username\": \"${USERNAME}\", \"password\": \"${PASSWORD}\"}" \
    --silent --show-error --fail
  echo "User ${USERNAME} created."
else
  echo "User ${USERNAME} already exists, skipping."
fi

# Create workspace if not exists
WORKSPACE_ID=$(
  curl "${MLFLOW_URL}/api/3.0/mlflow/workspaces" \
    --user "${ADMIN}" \
    --silent --show-error --fail |
    jq --raw-output --arg workspace "${WORKSPACE_NAME}" 'first(.workspaces[] | select(.name == $workspace) | .id) // empty'
)

if [ -z "$WORKSPACE_ID" ]; then
  echo "Creating workspace: ${WORKSPACE_NAME}"
  WORKSPACE_ID=$(
    curl --request POST "${MLFLOW_URL}/api/3.0/mlflow/workspaces" \
      --user "${ADMIN}" \
      --header "Content-Type: application/json" \
      --data "{\"name\": \"${WORKSPACE_NAME}\"}" \
      --silent --show-error --fail |
      jq --raw-output '.workspace.id // empty'
  )
  if [ -z "$WORKSPACE_ID" ]; then
    echo "Failed to create ${WORKSPACE_NAME} workspace." 1>&2
    exit 1
  fi
  echo "Workspace ${WORKSPACE_NAME} created (id: ${WORKSPACE_ID})."
else
  echo "Workspace ${WORKSPACE_NAME} already exists (id: ${WORKSPACE_ID}), skipping."
fi

# Grant edit permission if not set
PERMISSION=$(
  curl "${MLFLOW_URL}/api/3.0/mlflow/workspaces/${WORKSPACE_ID}/permissions" \
    --user "${ADMIN}" \
    --silent --show-error --fail |
    jq --raw-output --arg user "${USERNAME}" 'first(.permissions[] | select(.username == $user) | .permission) // empty'
)

if [ "$PERMISSION" != "EDIT" ]; then
  echo "Granting EDIT permission to ${USERNAME} on workspace ${WORKSPACE_ID}."
  curl --request POST "${MLFLOW_URL}/api/3.0/mlflow/workspaces/${WORKSPACE_ID}/permissions" \
    --user "${ADMIN}" \
    --header "Content-Type: application/json" \
    --data "{\"username\": \"${USERNAME}\", \"permission\": \"EDIT\"}" \
    --silent --show-error --fail
  echo "Permission granted."
else
  echo "User ${USERNAME} already has EDIT permission, skipping."
fi

echo "Done."