# TODO - 11/08/2026 - Continue here...
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

resource "kubernetes_config_map" "eks_teams" {
  for_each = local.eks.users.teams

  metadata {
    name      = "BASE"
    namespace = each.value.kubernetes.namespace
  }

  data = {
    # POSTGRES
    PGHOST = local.rds.postgresql.host
    PGPORT = local.rds.postgresql.port
    PGDATABASE = local.rds.postgresql.db_name
    # S3 / MWAA
    AWS_DEFAULT_REGION = local.aws.users.admin.region
    # MWAA
    AWS_ENDPOINT_URL_MWAA = local.mwaa.url.egress
    MWAA_ENVIRONMENT_NAME = local.mwaa.users.teams[each.key].environment.name # Not Fixed
    # MLFLOW
    MLFLOW_TRACKING_URI = local.mlflow.url.egress
    # SLACK (TEAM CREATED)
    # SLACK_CHANNEL_ID = ""
  }
}

resource "kubernetes_secret" "eks_teams" {
  for_each = local.eks.users.teams
  type     = "Opaque"

  metadata {
    name      = "BASE"
    namespace = each.value.kubernetes.namespace
  }

  data = {
    # POSTGRES
    PGUSER = local.rds.postgresql.users.teams[each.key].username
    PGPASSWORD = local.rds.postgresql.users.teams[each.key].password
    # S3 / MWAA
    AWS_ACCESS_KEY_ID = local.aws.users.teams[each.key].username
    AWS_SECRET_ACCESS_KEY = local.aws.users.teams[each.key].password
    # MLFLOW
    MLFLOW_TRACKING_USERNAME = local.mlflow.users.teams[each.key].username
    MLFLOW_TRACKING_PASSWORD = local.mlflow.users.teams[each.key].password
    # SLACK (TEAM CREATED)
    # SLACK_BOT_TOKEN = ""
    # SLACK_APP_TOKEN = ""
    # SLACK_SIGNING_SECRET = ""
  }
}
# MWAA CONNECTIONS
resource "aws_secretsmanager_secret" "postgres_connection" {
  for_each = local.rds.postgresql.users.teams
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_connections.postgres_id}"
}
resource "aws_secretsmanager_secret_version" "postgres_connection" {
  for_each = aws_secretsmanager_secret.postgres_connection
  secret_id = each.value.id

  secret_string = jsonencode({
   conn_type = "postgres",
   host = local.rds.postgresql.host,
   port = local.rds.postgresql.port,
   login = local.rds.postgresql.users.teams[each.key].username,
   password = local.rds.postgresql.users.teams[each.key].password,
   schema = local.rds.postgresql.db_name
  })

  depends_on = [aws_secretsmanager_secret.postgres_connection]
}
resource "aws_secretsmanager_secret" "s3_connection" {
  for_each = local.s3.users.teams
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_connections.s3_id}"
}
resource "aws_secretsmanager_secret_version" "s3_connection" {
  for_each = aws_secretsmanager_secret.s3_connection
  secret_id = each.value.id

  secret_string = jsonencode({
   conn_type = "aws",
   login = local.aws.users.teams[each.key].username,
   password = local.aws.users.teams[each.key].password,
   extra = {
     region_name = local.aws.users.admin.region
   }
  })

  depends_on = [aws_secretsmanager_secret.s3_connection]
}
# MWAA VARIABLES
# > CONNECTION IDS
resource "aws_secretsmanager_secret" "postgres_connection_id" {
  for_each = aws_secretsmanager_secret.postgres_connection
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.connection_ids.postgres}"
}
resource "aws_secretsmanager_secret_version" "postgres_connection_id" {
  for_each = aws_secretsmanager_secret.postgres_connection_id
  secret_id = each.value.id

  secret_string = local.mwaa_connections.postgres_id

  depends_on = [aws_secretsmanager_secret.postgres_connection_id]
}
resource "aws_secretsmanager_secret" "s3_connection_id" {
  for_each = aws_secretsmanager_secret.s3_connection
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.connection_ids.postgres}"
}
resource "aws_secretsmanager_secret_version" "s3_connection_id" {
  for_each = aws_secretsmanager_secret.s3_connection_id
  secret_id = each.value.id

  secret_string = local.mwaa_connections.s3_id

  depends_on = [aws_secretsmanager_secret.s3_connection_id]
}
# > MLFLOW
resource "aws_secretsmanager_secret" "mlflow_tracking_uri" {
  for_each = local.mlflow.users.teams
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.mlflow_ids.uri}"
}
resource "aws_secretsmanager_secret_version" "mlflow_tracking_uri" {
  for_each = aws_secretsmanager_secret.mlflow_tracking_uri
  secret_id = each.value.id

  secret_string = local.mlflow.url.ingress

  depends_on = [aws_secretsmanager_secret.mlflow_tracking_uri]
}
resource "aws_secretsmanager_secret" "mlflow_tracking_username" {
  for_each = local.mlflow.users.teams
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.mlflow_ids.username}"
}
resource "aws_secretsmanager_secret_version" "mlflow_tracking_username" {
  for_each = aws_secretsmanager_secret.mlflow_tracking_username
  secret_id = each.value.id

  secret_string = local.mlflow.users.teams[each.key].username

  depends_on = [aws_secretsmanager_secret.mlflow_tracking_username]
}
resource "aws_secretsmanager_secret" "mlflow_tracking_password" {
  for_each = local.mlflow.users.teams
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.mlflow_ids.password}"
}
resource "aws_secretsmanager_secret_version" "mlflow_tracking_password" {
  for_each = aws_secretsmanager_secret.mlflow_tracking_password
  secret_id = each.value.id

  secret_string = local.mlflow.users.teams[each.key].password

  depends_on = [aws_secretsmanager_secret.mlflow_tracking_password]
}
# > MWAA
resource "aws_secretsmanager_secret" "mwaa_dag_s3_uri" {
  for_each = local.mwaa.users.teams
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.mwaa_ids.dag_s3_uri}"
}
resource "aws_secretsmanager_secret_version" "mwaa_dag_s3_uri" {
  for_each = aws_secretsmanager_secret.mwaa_dag_s3_uri
  secret_id = each.value.id

  secret_string = local.mwaa.dag_s3_uri

  depends_on = [aws_secretsmanager_secret.mwaa_dag_s3_uri]
}
# ECR
resource "kubernetes_secret" "ecr_registry" {
  for_each = local.eks.users.teams
  type     = "kubernetes.io/dockerconfigjson"

  metadata {
    name      = "ECR_DOCKERCONFIGJSON"
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
# PLATFORM RESOURCES PROTECTION
resource "kubernetes_manifest" "platform_resources_protection" {
  for_each = local.eks.users.teams

  manifest = {
    apiVersion = "kyverno.io/v1"
    kind       = "Policy"
    metadata = {
      name      = "${each.key}_PLATFORM_RESOURCES_PROTECTION"
      namespace = each.value.kubernetes.namespace
    }
    spec = {
      rules = [
        {
          name = "PLATFORM_CONFIG_MAP_PROTECTION"
          match = {
            any = [{
              resources = {
                kinds      = ["ConfigMap"]
                names      = [kubernetes_config_map.eks_teams[each.key].metadata[0].name]
                operations = ["UPDATE", "DELETE"]
              }
            }]
          }
          exclude = {
            any = [{
              clusterRoles = ["cluster-admin"]
            }]
          }
          validate = {
            message = "Platform-managed ConfigMap cannot be modified."
            deny    = {}
          }
        },
        {
          name = "PLATFORM_SECRET_PROTECTION"
          match = {
            any = [{
              resources = {
                kinds = ["Secret"]
                names = [
                  kubernetes_secret.eks_teams[each.key].metadata[0].name,
                  kubernetes_secret.ecr_registry[each.key].metadata[0].name,
                ]
                operations = ["UPDATE", "DELETE"]
              }
            }]
          }
          exclude = {
            any = [{
              clusterRoles = ["cluster-admin"]
            }]
          }
          validate = {
            message = "Platform-managed Secret cannot be modified."
            deny    = {}
          }
        }
      ]
    }
  }

  depends_on = [
    kubernetes_config_map.eks_teams,
    kubernetes_secret.eks_teams,
    kubernetes_secret.ecr_registry,
  ]
}