locals {
  # Shared by every DAG container (drift_monitor, training_pipeline, archiving)
  mle_runtime_secret = {
    POSTGRES_HOST             = var.rds_db_address
    POSTGRES_PORT             = var.rds_db_port
    POSTGRES_USER             = var.mle_db_username
    POSTGRES_PASSWORD         = var.mle_db_password
    FRAUD_DETECTION_DB_NAME   = var.rds_db_name

    S3_ENDPOINT_URL           = var.s3_endpoint_url
    S3_ACCESS_KEY             = var.s3_access_key
    S3_SECRET_KEY             = var.s3_secret_key
    AWS_DEFAULT_REGION        = var.s3_aws_region
    S3_MLE_BUCKET             = var.s3_mle_bucket
    MLFLOW_S3_ENDPOINT_URL    = var.s3_endpoint_url

    MLFLOW_TRACKING_URI       = var.mlflow_tracking_uri
    MLFLOW_EXPERIMENT_NAME    = "fraud-detection"

    SLACK_BOT_USER_AUTH_TOKEN = var.slack_bot_token
    SLACK_CHANNEL_ID          = var.slack_channel_id

    FRAUD_API_URL             = var.fraud_api_url
  }

  # fraud_api only
  fraud_api_secret = {
    POSTGRES_HOST             = var.rds_db_address
    POSTGRES_PORT             = var.rds_db_port
    POSTGRES_USER             = var.mle_db_username
    POSTGRES_PASSWORD         = var.mle_db_password
    FRAUD_DETECTION_DB_NAME   = var.rds_db_name

    MLFLOW_TRACKING_URI       = var.mlflow_tracking_uri
    MLFLOW_MODEL_URI          = var.mlflow_model_uri
    MLFLOW_S3_ENDPOINT_URL    = var.s3_endpoint_url

    SLACK_BOT_USER_AUTH_TOKEN = var.slack_bot_token
    SLACK_APP_LEVEL_TOKEN     = var.slack_app_token
    SLACK_CHANNEL_ID          = var.slack_channel_id
    SLACK_SIGNING_SECRET      = var.slack_signing_secret
  }
}

resource "aws_secretsmanager_secret" "mle_runtime" {
  name                    = "/fraud-detection/mle-runtime"
  recovery_window_in_days = 0   # immediate delete in ministack
}

resource "aws_secretsmanager_secret_version" "mle_runtime" {
  secret_id     = aws_secretsmanager_secret.mle_runtime.id
  secret_string = jsonencode(local.mle_runtime_secret)
}

resource "aws_secretsmanager_secret" "fraud_api" {
  name                    = "/fraud-detection/fraud-api"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "fraud_api" {
  secret_id     = aws_secretsmanager_secret.fraud_api.id
  secret_string = jsonencode(local.fraud_api_secret)
}