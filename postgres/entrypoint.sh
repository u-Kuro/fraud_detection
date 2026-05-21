#!/bin/bash
set -e

# Run the original postgres entrypoint in background with logs
/usr/local/bin/docker-entrypoint.sh postgres -c log_connections=on -c log_min_messages=info &
PGPID=$!

# Wait until ready
until pg_isready -U "$POSTGRES_USER"; do sleep 1; done

echo "Checking and initializing databases..."
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -c "CREATE DATABASE \"$MLFLOW_DB\";" || true
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -c "CREATE DATABASE \"$FRAUD_DETECTION_DB\";" || true
echo "Checking/initializing schema file on $FRAUD_DETECTION_DB..."
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$FRAUD_DETECTION_DB" -f ./fraud_detection/schema.sql
echo "Checking/initializing seed file on $FRAUD_DETECTION_DB..."
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$FRAUD_DETECTION_DB" -f ./fraud_detection/seed.sql
echo "All databases initialized successfully!"

# Hand back to postgres
wait $PGPID