# INPUTS
locals {
  aws    = var.aws
  ecr    = var.ecr
  eks    = var.eks
  mlflow = var.mlflow
  mwaa   = var.mwaa
  rds    = var.rds
  s3     = var.s3
}
# COMPUTED
locals {
  # MWAA
  mwaa_connections = {
    postgres_id = "POSTGRES"
    s3_id       = "S3"
  }
  # For secretsmanager variables (Prefixed with AIRFLOW_VAR_ so Fixed won't work)
  mwaa_variables = {
    connection_ids = {
      # GITHUB (TEAM CREATED)
      # github = "GITHUB_CONNECTION_ID"
      # github = jsonencode({
      #  "conn_type": "http",
      #  "host": "https://api.github.com",
      #  "extra": {
      #    "headers": {
      #      "Authorization": "Bearer ghp_YourGitHubPersonalAccessTokenHere",
      #      "Accept": "application/vnd.github+json",
      #      "X-GitHub-Api-Version": "2022-11-28"
      #    }
      #  }
      # })
      postgres = "POSTGRES_CONNECTION_ID"
      s3       = "S3_CONNECTION_ID"
      # SLACK (TEAM CREATED)
      # slack = "SLACK_CONNECTION_ID"
      # slack = jsonencode({
      #   "conn_type": "slack",
      #   "password": "YOUR_SLACK_BOT_TOKEN"
      # })
    }
    # GITHUB (TEAM CREATED)
    # github_ids = {
    #   owner = "GITHUB_OWNER"
    #   repository = "GITHUB_REPOSITORY"
    # }
    # MLFLOW (Fixed won't work)
    mlflow_ids = {
      uri      = "MLFLOW_TRACKING_URI" # Ingress
      username = "MLFLOW_TRACKING_USERNAME"
      password = "MLFLOW_TRACKING_PASSWORD"
    }
    # MWAA
    mwaa_ids = {
      dag_s3_uri = "MWAA_DAG_S3_URI"
    }
    # SLACK (TEAM CREATED)
    # slack_ids = {
    #   channel_id = "SLACK_CHANNEL_ID"
    # }
  }
}