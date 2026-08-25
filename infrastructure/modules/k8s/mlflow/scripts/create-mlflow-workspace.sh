#!/bin/sh
set -e

# install curl and jq
apk add --no-cache curl jq > /dev/null 2>&1

# Create user if not exists
USER_STATUS=$( \
  curl -s -o /dev/null -w "%{http_code}" \
  "${MLFLOW_URL}/api/2.0/mlflow/users/get?username=${USERNAME}" \
  -u "${ADMIN}" \
)

if [ "$USER_STATUS" != "200" ]; then
  echo "Creating user: ${USERNAME}"
  curl -sf -X POST "${MLFLOW_URL}/api/2.0/mlflow/users/create" \
    -u "${ADMIN}" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${USERNAME}\", \"password\": \"${PASSWORD}\"}"
else
  echo "User ${USERNAME} already exists, skipping."
fi

# Create workspace if not exists
WORKSPACE_ID=$( \
  curl -sf "${MLFLOW_URL}/api/3.0/mlflow/workspaces" \
  -u "${ADMIN}" | \
  jq -r ".workspaces[] | select(.name == \"${WORKSPACE_NAME}\") | .id" \
)

if [ -z "$WORKSPACE_ID" ]; then
  echo "Creating workspace: ${WORKSPACE_NAME}"
  WORKSPACE_ID=$( \
    curl -sf -X POST "${MLFLOW_URL}/api/3.0/mlflow/workspaces" \
    -u "${ADMIN}" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"${WORKSPACE_NAME}\"}" | jq -r '.workspace.id' \
  )
else
  echo "Workspace ${WORKSPACE_NAME} already exists (id: ${WORKSPACE_ID}), skipping."
fi

# Grant edit permission if not set
PERMISSION=$( \
  curl -sf "${MLFLOW_URL}/api/3.0/mlflow/workspaces/${WORKSPACE_ID}/permissions" \
  -u "${ADMIN}" | \
  jq -r ".permissions[] | select(.username == \"${USERNAME}\") | .permission // empty" \
)
if [ "$PERMISSION" != "EDIT" ]; then
  echo "Granting permission to ${USERNAME} on workspace ${WORKSPACE_ID}"
  curl -sf -X POST "${MLFLOW_URL}/api/3.0/mlflow/workspaces/${WORKSPACE_ID}/permissions" \
    -u "${ADMIN}" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${USERNAME}\", \"permission\": \"EDIT\"}"
else
  echo "User is already permitted, skipping."
fi