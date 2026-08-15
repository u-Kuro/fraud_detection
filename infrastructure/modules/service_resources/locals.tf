# URLs
# url - http://[$container_ip]:[$port|4566]
# ingress_url - http://[alb-dns]/[deployment-path] or http://[$container_ip]:[node-port]
# egress_url - http://[$gateway_ip]:[$port|4566]
# intra_url (same-namespace) - http://[service-name]:[port]
# inter_url (cross-namespace) - http://[service-name].[namespace].svc.cluster.local:[port]

# URIs
# s3_egress - aws --endpoint-url http://[$gateway_ip]:[$port|4566] s3 cp s3://my-bucket/file
# postgres_egress - psql postgresql://admin:password@[$gateway_ip]:[$rds_host_port|15432]/mydb

# INPUTS
locals {
  iam    = var.iam
  ecr    = var.ecr
  eks    = var.eks
  mlflow = var.mlflow
  mwaa   = var.mwaa
  rds    = var.rds
  s3     = var.s3
}
# COMPUTED
locals {
  # KUBERNETES RESOURCES
  kubernetes_resources = {
    config_map = {
      base = {
        name = "base"
      }
    }
    secret = {
      base = {
        name = "base"
      }
      docker_config_json = {
        name = "docker-config-json"
      }
    }
  }
  # MWAA
  mwaa_connections = {
    postgres_id = "POSTGRES"
    s3_id       = "S3"
  }
  # For secrets manager variables (Prefixed with AIRFLOW_VAR_ so Fixed won't work)
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
    # KUBERNETES (Fixed won't work)
    kubernetes_resources_ids = {
      config_map = {
        base = "KUBERNETES_CONFIG_MAP_BASE_NAME"
      }
      secret = {
        base               = "KUBERNETES_SECRET_BASE_NAME"
        docker_config_json = "KUBERNETES_SECRET_DOCKER_CONFIG_JSON_NAME"
      }
    }
    # MLFLOW (Fixed won't work)
    mlflow_ids = {
      uri      = "MLFLOW_TRACKING_URI" # Ingress
      username = "MLFLOW_TRACKING_USERNAME"
      password = "MLFLOW_TRACKING_PASSWORD"
    }
    # SLACK (TEAM CREATED)
    # slack_ids = {
    #   channel_id = "SLACK_CHANNEL_ID"
    # }
  }
}