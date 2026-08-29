# URLs
# url - http://[$container_ip]:[$port|4566]
# ingress_url - http://[alb-dns]/[deployment-path] or http://[$container_ip]:[node-port]
# egress_url - http://[$gateway_ip]:[$port|4566]
# intra_url (same-namespace) - http://[service-name]:[port]
# inter_url (cross-namespace) - http://[service-name].[namespace].svc.cluster.local:[port]

# URIs
# s3_egress - aws --endpoint-url http://[$gateway_ip]:[$port|4566] s3 cp s3://my-bucket/file
# postgres_egress - psql postgresql://admin:password@[$gateway_ip]:[$rds_host_port|15432]/mydb

# What else are essential

# DAGs (secretsmanager) - DONE CHECKING
# 1) postgres connection - ok
# 2) Slack connection + slack channel id - user created
# 3) mlflow url and credentials - ok
# 4) kubernetes connection - ok
# 4.5) kubernetes namespace - ok
# 5) repo images (multiple depends on teams repo) - user created (e.g. drift_check:latest)
# 6) k8s docker registry - ok
# 7) k8s docker registry name - ok
# 8) k8s base config map - ok
# 9) k8s base config map name - ok
# 10) k8s base secret - ok
# 11) k8s base secret name - ok
# 12) github_connection - user created
# 13) github_connection name - user created
# 14) github variable headers auth token - user created

# Services
# 1) slack_bot_token (user created)
# 2) slack_app_token (user created)
# 3) slack_signing_secret (user created)
# 4) slack_channel_id (user created)
# 5) aws region - ok
# 6) aws access key - ok
# 7) aws secret access key - ok
# 8) aws endpoint s3 url - ok
# 9) s3 bucket (mle) - ok
# 10) aws endpoint mwaa url - ok
# 11) mwaa environment name - ok
# 12) postgres host - ok
# 13) postgres port - ok
# 14) postgres db - ok
# 15) postgres username - ok
# 16) postgres password - ok
# 17) mlflow tracking uri - ok

# GitHub Workflows
# 1) airflow container name - ok
# 2) airflow dag directory path - ok
# 3) aws region - shared for .secrets
# 4) aws access key - shared for .secrets
# 5) aws secret access key - shared for .secrets
# 6) aws endpoint url - shared for .secrets
# 7) postgres version for atlas lint --dev-url - ok
# 8) postgres credential+endpoint in 1 uri string - ok
# 9) kubeconfig - ok

# DAGs
# CI test | CD copy dags

# DB
# CI atlas migrate lint | CD atlas migrate apply

# Services
# CI test + docker build (load=true & push=false) > run | CD docker build (load=false & push=true) + deploy to k8s (requires workflow_dispatch for fraud detection api)

# 0) (can't be done in act) add branch protection rules for main to avoid merging before CI passed
# 1) dev open pull req (branch to main)
# 2) ci run tests (using PR merge reference)
# 3) (can't be done in act) merge accepted and pushed to main
# 4) cd runs for deployment

locals {
  # EKS
  # /resource-names
  eks_k8s_base_config_map_name        = "base"
  eks_k8s_base_secret_name            = "base"
  eks_k8s_docker_registry_secret_name = "docker-registry"

  # MWAA
  # /connections
  mwaa_connections_k8s_connection_id      = "k8s"
  mwaa_connections_postgres_connection_id = "postgres"
  mwaa_connections_s3_connection_id       = "s3"
  # /variables (Prefixed with AIRFLOW_VAR_ so Fixed won't work)
  mwaa_variables_k8s_connection_id_name          = "K8S_CONNECTION_ID"
  mwaa_variables_k8s_namespace                   = "K8S_NAMESPACE"
  mwaa_variables_k8s_base_config_map_name        = "K8S_BASE_CONFIG_MAP_NAME"
  mwaa_variables_k8s_base_secret_name            = "K8S_BASE_SECRET_NAME"
  mwaa_variables_k8s_docker_registry_secret_name = "K8S_DOCKER_REGISTRY_SECRET_NAME"

  mwaa_variables_mlflow_tracking_uri      = "MLFLOW_TRACKING_URI"
  mwaa_variables_mlflow_tracking_username = "MLFLOW_TRACKING_USERNAME"
  mwaa_variables_mlflow_tracking_password = "MLFLOW_TRACKING_PASSWORD"

  mwaa_variables_postgres_connection_id_name = "POSTGRES_CONNECTION_ID"

  mwaa_variables_s3_connection_id_name = "S3_CONNECTION_ID"
  mwaa_variables_s3_bucket             = "S3_BUCKET"

  # GitHub (team created)
  # github = "GITHUB_CONNECTION_ID"
  # github = jsonencode({
  #  "conn_type": "http",
  #  "host": "api.github.com",
  #  "extra": {
  #    "headers": {
  #      "Authorization": "Bearer ghp_YourGitHubPersonalAccessTokenHere",
  #      "Accept": "application/vnd.github+json",
  #      "X-GitHub-Api-Version": "2022-11-28"
  #    }
  #  }
  # })

  # Slack (team created)
  # slack = "SLACK_CONNECTION_ID"
  # slack = jsonencode({
  #   "conn_type": "slack",
  #   "password": "YOUR_SLACK_BOT_TOKEN"
  # })

  # Slack (team created)
  # slack_ids = {
  #   channel_id = "SLACK_CHANNEL_ID"
  # }
}