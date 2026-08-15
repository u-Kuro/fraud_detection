# MWAA / Nektos /

# EKS TEAMS' CONFIG MAPS
resource "kubernetes_config_map" "eks_teams_base_config_map" {
  for_each = local.eks.users.teams

  metadata {
    name      = local.kubernetes_resources.config_map.base.name
    namespace = each.value.kubernetes.namespace
  }

  data = {
    # POSTGRES
    PGHOST     = var.rds_postgres_egress_host # [$gateway_ip]
    PGPORT     = var.rds_postgres_egress_port # [$rds_host_port|15432]
    PGDATABASE = local.rds.postgres.db_name
    # S3 / MWAA
    AWS_ENDPOINT_URL   = var.s3_egress_url # http://[$gateway_ip]:[$port|4566] - For all stuff in boto e.g. s3 or dynamodb
    AWS_DEFAULT_REGION = local.iam.users.admin.region
    # MWAA
    AWS_ENDPOINT_URL_MWAA = var.mwaa_egress_url
    MWAA_ENVIRONMENT_NAME = local.mwaa.users.teams[each.key].environment.name # Not Fixed
    # MLFLOW
    MLFLOW_TRACKING_URI = var.mlflow_inter_url # http://[service-name].[namespace].svc.cluster.local:[port]
    # SLACK (TEAM CREATED)
    # SLACK_CHANNEL_ID = ""
  }
}
# EKS TEAMS' SECRETS
resource "kubernetes_secret" "eks_teams_base_secret" {
  for_each = local.eks.users.teams
  type     = "Opaque"

  metadata {
    name      = local.kubernetes_resources.secret.base.name
    namespace = each.value.kubernetes.namespace
  }

  data = {
    # POSTGRES
    PGUSER     = local.rds.postgres.users.teams[each.key].username
    PGPASSWORD = local.rds.postgres.users.teams[each.key].password
    # S3 / MWAA
    AWS_ACCESS_KEY_ID     = local.iam.users.teams[each.key].username
    AWS_SECRET_ACCESS_KEY = local.iam.users.teams[each.key].password
    # MLFLOW
    MLFLOW_TRACKING_USERNAME = local.mlflow.users.teams[each.key].username
    MLFLOW_TRACKING_PASSWORD = local.mlflow.users.teams[each.key].password
    # SLACK (TEAM CREATED)
    # SLACK_BOT_TOKEN = ""
    # SLACK_APP_TOKEN = ""
    # SLACK_SIGNING_SECRET = ""
  }
}
# EKS TEAMS' DOCKER CONFIG JSON
resource "kubernetes_secret" "eks_teams_docker_config_json" {
  for_each = local.eks.users.teams
  type     = "kubernetes.io/dockerconfigjson"

  metadata {
    name      = local.kubernetes_resources.secret.docker_config_json.name
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
# MWAA CONNECTIONS
# > TEAMS' POSTGRES CONNECTION
resource "aws_secretsmanager_secret" "postgres_connection" {
  for_each = local.rds.postgres.users.teams
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_connections.postgres_id}"
}
resource "aws_secretsmanager_secret_version" "postgres_connection" {
  for_each  = aws_secretsmanager_secret.postgres_connection
  secret_id = each.value.id

  secret_string = jsonencode({
    conn_type = "postgres",
    host      = local.rds.postgres.host,
    port      = local.rds.postgres.port,
    login     = local.rds.postgres.users.teams[each.key].username,
    password  = local.rds.postgres.users.teams[each.key].password,
    schema    = local.rds.postgres.db_name
  })

  depends_on = [aws_secretsmanager_secret.postgres_connection]
}
# > TEAMS' S3 CONNECTION
resource "aws_secretsmanager_secret" "s3_connection" {
  for_each = local.s3.users.teams
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_connections.s3_id}"
}
resource "aws_secretsmanager_secret_version" "s3_connection" {
  for_each  = aws_secretsmanager_secret.s3_connection
  secret_id = each.value.id

  secret_string = jsonencode({
    conn_type = "aws",
    login     = local.iam.users.teams[each.key].username,
    password  = local.iam.users.teams[each.key].password,
    extra = {
      region_name = local.iam.users.admin.region
    }
  })

  depends_on = [aws_secretsmanager_secret.s3_connection]
}
# MWAA VARIABLES
# > EKS TEAMS' KUBERNETES RESOURCE NAMES
resource "aws_secretsmanager_secret" "eks_teams_base_config_map" {
  for_each = kubernetes_config_map.eks_teams_base_config_map
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.kubernetes_resources_ids.config_map.base}"

  depends_on = [kubernetes_config_map.eks_teams_base_config_map]
}
resource "aws_secretsmanager_secret_version" "eks_teams_base_config_map" {
  for_each  = aws_secretsmanager_secret.eks_teams_base_config_map
  secret_id = each.value.id

  secret_string = kubernetes_config_map.eks_teams_base_config_map.metadata[0].name

  depends_on = [
    kubernetes_config_map.eks_teams_base_config_map,
    aws_secretsmanager_secret.eks_teams_base_config_map
  ]
}
resource "aws_secretsmanager_secret" "eks_teams_base_secret" {
  for_each = kubernetes_secret.eks_teams_base_secret
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.kubernetes_resources_ids.secret.base}"

  depends_on = [kubernetes_secret.eks_teams_base_secret]
}
resource "aws_secretsmanager_secret_version" "eks_teams_base_secret" {
  for_each  = aws_secretsmanager_secret.eks_teams_base_secret
  secret_id = each.value.id

  secret_string = kubernetes_secret.eks_teams_base_secret.metadata[0].name

  depends_on = [
    kubernetes_secret.eks_teams_base_secret,
    aws_secretsmanager_secret.eks_teams_base_secret
  ]
}
resource "aws_secretsmanager_secret" "eks_teams_docker_config_json" {
  for_each = kubernetes_secret.eks_teams_docker_config_json
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.kubernetes_resources_ids.secret.docker_config_json}"

  depends_on = [kubernetes_secret.eks_teams_docker_config_json]
}
resource "aws_secretsmanager_secret_version" "eks_teams_docker_config_json" {
  for_each  = aws_secretsmanager_secret.eks_teams_docker_config_json
  secret_id = each.value.id

  secret_string = kubernetes_secret.eks_teams_docker_config_json.metadata[0].name

  depends_on = [
    kubernetes_secret.eks_teams_docker_config_json,
    aws_secretsmanager_secret.eks_teams_docker_config_json
  ]
}
# > MWAA TEAMS' CONNECTION IDS
resource "aws_secretsmanager_secret" "postgres_connection_id" {
  for_each = aws_secretsmanager_secret.postgres_connection
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.connection_ids.postgres}"

  depends_on = [aws_secretsmanager_secret.postgres_connection]
}
resource "aws_secretsmanager_secret_version" "postgres_connection_id" {
  for_each  = aws_secretsmanager_secret.postgres_connection_id
  secret_id = each.value.id

  secret_string = local.mwaa_connections.postgres_id

  depends_on = [
    aws_secretsmanager_secret.postgres_connection,
    aws_secretsmanager_secret.postgres_connection_id
  ]
}
resource "aws_secretsmanager_secret" "s3_connection_id" {
  for_each = aws_secretsmanager_secret.s3_connection
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.connection_ids.postgres}"

  depends_on = [aws_secretsmanager_secret.s3_connection]
}
resource "aws_secretsmanager_secret_version" "s3_connection_id" {
  for_each  = aws_secretsmanager_secret.s3_connection_id
  secret_id = each.value.id

  secret_string = local.mwaa_connections.s3_id

  depends_on = [
    aws_secretsmanager_secret.s3_connection,
    aws_secretsmanager_secret.s3_connection_id
  ]
}
# > MLFLOW TEAMS
resource "aws_secretsmanager_secret" "mlflow_tracking_uri" {
  for_each = local.mlflow.users.teams
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.mlflow_ids.uri}"
}
resource "aws_secretsmanager_secret_version" "mlflow_tracking_uri" {
  for_each  = aws_secretsmanager_secret.mlflow_tracking_uri
  secret_id = each.value.id

  secret_string = var.mlflow_ingress_url

  depends_on = [aws_secretsmanager_secret.mlflow_tracking_uri]
}
resource "aws_secretsmanager_secret" "mlflow_tracking_username" {
  for_each = local.mlflow.users.teams
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.mlflow_ids.username}"
}
resource "aws_secretsmanager_secret_version" "mlflow_tracking_username" {
  for_each  = aws_secretsmanager_secret.mlflow_tracking_username
  secret_id = each.value.id

  secret_string = local.mlflow.users.teams[each.key].username

  depends_on = [aws_secretsmanager_secret.mlflow_tracking_username]
}
resource "aws_secretsmanager_secret" "mlflow_tracking_password" {
  for_each = local.mlflow.users.teams
  name     = "${local.mwaa.users.teams[each.key].connections.prefix}/${local.mwaa_variables.mlflow_ids.password}"
}
resource "aws_secretsmanager_secret_version" "mlflow_tracking_password" {
  for_each  = aws_secretsmanager_secret.mlflow_tracking_password
  secret_id = each.value.id

  secret_string = local.mlflow.users.teams[each.key].password

  depends_on = [aws_secretsmanager_secret.mlflow_tracking_password]
}
# PLATFORM RESOURCES PROTECTION
resource "kubernetes_manifest" "platform_resources_protection" {
  for_each = local.eks.users.teams

  manifest = {
    apiVersion = "kyverno.io/v1"
    kind       = "Policy"
    metadata = {
      name      = "${each.key}-platform-resources-protection"
      namespace = each.value.kubernetes.namespace
    }
    spec = {
      rules = [
        {
          name = "platform-config-map-protection"
          match = {
            any = [{
              resources = {
                kinds      = ["ConfigMap"]
                names      = [kubernetes_config_map.eks_teams_base_config_map[each.key].metadata[0].name]
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
          name = "platform-secret-protection"
          match = {
            any = [{
              resources = {
                kinds = ["Secret"]
                names = [
                  kubernetes_secret.eks_teams_base_secret[each.key].metadata[0].name,
                  kubernetes_secret.eks_teams_docker_config_json[each.key].metadata[0].name,
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
    kubernetes_config_map.eks_teams_base_config_map,
    kubernetes_secret.eks_teams_base_secret,
    kubernetes_secret.eks_teams_docker_config_json,
  ]
}