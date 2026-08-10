# TODO - 10/08/2026 - Continue here...
# ingress
# - MWAA to mlflow-pod (real aws use alb/elb) so try to create one
# egress
# - POD to S3 (real aws calls https directly) so just use docker network ip (dns does not work)
# POD calls
# - Postgres
# - S3
# - MWAA
# - Slack
# - MLFLOW x
# MWAA calls
# - POD
# - GitHub (act)
# - Slack
# - Postgres x
# - S3 x
# - Secret Manager x
# - ECR x
# - EKS x
# Slack Calls
# - POD

resource "kubernetes_config_map" "teams" {
  for_each = local.aws.users.teams

  metadata {
    name      = "base"
    namespace = each.value.kubernetes.namespace
  }

  data = {
    # POSTGRES
    PGHOST = ""
    PGPORT = ""
    PGUSER = ""
    PGPASSWORD = ""
    PGDATABASE = ""
    # S3 / MWAA
    AWS_ACCESS_KEY_ID = ""
    AWS_SECRET_ACCESS_KEY = ""
    AWS_DEFAULT_REGION = ""
    # MWAA
    AWS_ENDPOINT_URL_MWAA = ""
    MWAA_ENVIRONMENT_NAME = "" # Not Fixed
    # MLFLOW
    MLFLOW_TRACKING_URI = "" # Internal
    MLFLOW_TRACKING_USERNAME = ""
    MLFLOW_TRACKING_PASSWORD = ""
    # SLACK (TEAM CREATED)
    # SLACK_BOT_TOKEN = ""
    # SLACK_APP_TOKEN = ""
    # SLACK_SIGNING_SECRET = ""
    # SLACK_CHANNEL_ID = ""

    # For secretsmanager connection
    # POSTGRES
    postgres = {
     "conn_type": "postgres",
     "host": "PGHOST",
     "port": 0,
     "login": "PGUSER",
     "password": "PGPASSWORD",
     "schema": "PGDATABASE" # Unexpectedly called schema
    }
    # S3
    s3 = {
     "conn_type": "aws",
     "login": "AWS_ACCESS_KEY_ID",
     "password": "AWS_SECRET_ACCESS_KEY",
     "extra": {
       "region_name": "AWS_DEFAULT_REGION"
     }
    }
    # SLACK (TEAM CREATED)
    # slack = {
    #   "conn_type": "slack",
    #   "password": "YOUR_SLACK_BOT_TOKEN"
    # }
    # GITHUB (TEAM CREATED)
    # github = {
    #  "conn_type": "http",
    #  "host": "https://api.github.com",
    #  "extra": {
    #    "headers": {
    #      "Authorization": "Bearer ghp_YourGitHubPersonalAccessTokenHere",
    #      "Accept": "application/vnd.github+json",
    #      "X-GitHub-Api-Version": "2022-11-28"
    #    }
    #  }
    # }

    # For secretsmanager variables (Prefixed with AIRFLOW_VAR_ so Fixed won't work)
    # POSTGRES
    POSTGRES_CONNECTION_ID = ""
    # S3
    S3_CONNECTION_ID = ""
    # MLFLOW (Fixed won't work)
    MLFLOW_TRACKING_URI = "" # External
    MLFLOW_TRACKING_USERNAME = ""
    MLFLOW_TRACKING_PASSWORD = ""
    # GITHUB (TEAM CREATED)
    # GITHUB_CONNECTION_ID = ""
    # SLACK (TEAM CREATED)
    # SLACK_CONNECTION_ID = ""
    # SLACK_CHANNEL_ID = ""
  }
}

resource "kubernetes_secret" "teams" {
  for_each = local.aws.users.teams
  type     = "Opaque"

  metadata {
    name      = "base"
    namespace = each.value.kubernetes.namespace
  }

  data = {
    # SECRETS
  }
}

resource "kubernetes_secret" "ecr_registry" {
  for_each = local.aws.users.teams
  type     = "kubernetes.io/dockerconfigjson"

  metadata {
    name      = "ecr-dockerconfigjson"
    namespace = each.value.kubernetes.namespace
  }

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        # Matches to original endpoint in EKS. In MiniStack's EKS (registries.yaml), it's set to redirect to MiniStack's ECR endpoint.
        (local.ecr.aws.endpoint) = {
          username = local.ecr.aws.token.username
          password = local.ecr.aws.token.password
          auth     = local.ecr.aws.token.authorization_token
        }
      }
    })
  }
}