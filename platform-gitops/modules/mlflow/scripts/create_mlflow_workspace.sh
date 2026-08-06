#!/bin/sh
set -e

# install curl and jq
apk add --no-cache curl jq > /dev/null 2>&1

# Create user if not exists
USER_STATUS=$( \
  curl -s -o /dev/null -w "%{http_code}" \
  "${MLFLOW_TRACKING_URI}/api/2.0/mlflow/users/get?username=${TEAM}" \
  -u "${ADMIN}" \
)

if [ "$USER_STATUS" != "200" ]; then
  echo "Creating user: ${TEAM}"
  curl -sf -X POST "${MLFLOW_TRACKING_URI}/api/2.0/mlflow/users/create" \
    -u "${ADMIN}" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${TEAM}\", \"password\": \"${PASSWORD}\"}"
else
  echo "User ${TEAM} already exists, skipping."
fi

# Create workspace if not exists
WORKSPACE_NAME="${TEAM}_workspace"
WORKSPACE_ID=$( \
  curl -sf "${MLFLOW_TRACKING_URI}/api/3.0/mlflow/workspaces" \
  -u "${ADMIN}" | \
  jq -r ".workspaces[] | select(.name == \"${WORKSPACE_NAME}\") | .id" \
)

if [ -z "$WORKSPACE_ID" ]; then
  echo "Creating workspace: ${WORKSPACE_NAME}"
  WORKSPACE_ID=$( \
    curl -sf -X POST "${MLFLOW_TRACKING_URI}/api/3.0/mlflow/workspaces" \
    -u "${ADMIN}" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"${WORKSPACE_NAME}\"}" | jq -r '.workspace.id' \
  )
else
  echo "Workspace ${WORKSPACE_NAME} already exists (id: ${WORKSPACE_ID}), skipping."
fi

# Grant edit permission if not set
PERMISSION=$( \
  curl -sf "${MLFLOW_TRACKING_URI}/api/3.0/mlflow/workspaces/${WORKSPACE_ID}/permissions" \
  -u "${ADMIN}" | \
  jq -r ".permissions[] | select(.username == \"${TEAM}\") | .permission // empty" \
)
if [ "$PERMISSION" != "EDIT" ]; then
  echo "Granting permission to ${TEAM} on workspace ${WORKSPACE_ID}"
  curl -sf -X POST "${MLFLOW_TRACKING_URI}/api/3.0/mlflow/workspaces/${WORKSPACE_ID}/permissions" \
    -u "${ADMIN}" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${TEAM}\", \"permission\": \"EDIT\"}"
else
  echo "User is already permitted, skipping."
fi