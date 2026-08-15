# URLs
# url - http://[$container_ip]:[$port|4566]
# ingress_url - http://[alb-dns]/[deployment-path] or http://[$container_ip]:[node-port]
# egress_url - http://[$gateway_ip]:[$port|4566]
# intra_url (same-namespace) - http://[service-name]:[port]
# inter_url (cross-namespace) - http://[service-name].[namespace].svc.cluster.local:[port]

# URIs
# s3_egress - aws --endpoint-url http://[$gateway_ip]:[$port|4566] s3 cp s3://my-bucket/file
# postgres_egress - psql postgresql://admin:password@[$gateway_ip]:[$rds_host_port|15432]/mydb

locals {
  # EKS
  # /resource-names
  eks_k8s_base_config_map_name        = "base"
  eks_k8s_base_secret_name            = "base"
  eks_k8s_docker_registry_secret_name = "docker-registry"

  # MWAA
  # /connections
  mwaa_connections_postgres_connection_id = "postgres"
  mwaa_connections_s3_connection_id       = "s3"
  # /variables (Prefixed with AIRFLOW_VAR_ so Fixed won't work)
  mwaa_variables_postgres_connection_id = "POSTGRES_CONNECTION_ID"
  mwaa_variables_s3_connection_id       = "S3_CONNECTION_ID"

  mwaa_variables_k8s_base_config_map_name        = "K8S_BASE_CONFIG_MAP_NAME"
  mwaa_variables_k8s_base_secret_name            = "K8S_BASE_SECRET_NAME"
  mwaa_variables_k8s_docker_registry_secret_name = "K8S_DOCKER_REGISTRY_SECRET_NAME"

  mwaa_variables_mlflow_tracking_uri      = "MLFLOW_TRACKING_URI"
  mwaa_variables_mlflow_tracking_username = "MLFLOW_TRACKING_USERNAME"
  mwaa_variables_mlflow_tracking_password = "MLFLOW_TRACKING_PASSWORD"

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

  # GITHUB (TEAM CREATED)
  # github_ids = {
  #   owner = "GITHUB_OWNER"
  #   repository = "GITHUB_REPOSITORY"
  # }

  # SLACK (TEAM CREATED)
  # slack = "SLACK_CONNECTION_ID"
  # slack = jsonencode({
  #   "conn_type": "slack",
  #   "password": "YOUR_SLACK_BOT_TOKEN"
  # })

  # SLACK (TEAM CREATED)
  # slack_ids = {
  #   channel_id = "SLACK_CHANNEL_ID"
  # }
}