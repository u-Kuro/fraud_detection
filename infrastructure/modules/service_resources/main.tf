# TODO - 15/08/2026 - Continue here... recheck each value
# MWAA / Nektos /

# EKS TEAMS' CONFIG MAPS
resource "kubernetes_config_map" "eks_teams_base_config_map" {
  for_each = var.eks_teams

  metadata {
    name      = local.eks_k8s_base_config_map_name
    namespace = var.eks_teams_kubernetes_namespaces[each.key]
  }

  data = {
    # POSTGRES
    PGHOST     = var.rds_postgres_egress_host # [$gateway_ip]
    PGPORT     = var.rds_postgres_egress_port # [$rds_host_port|15432]
    PGDATABASE = var.rds_postgres_db_name
    # S3 / MWAA
    AWS_ENDPOINT_URL   = var.s3_egress_url # http://[$gateway_ip]:[$port|4566] - For all stuff in boto e.g. s3 or dynamodb
    AWS_DEFAULT_REGION = var.iam_admin_region
    # MWAA
    AWS_ENDPOINT_URL_MWAA = var.mwaa_egress_url
    MWAA_ENVIRONMENT_NAME = var.mwaa_teams_environment_names[each.key] # Not Fixed
    # MLFLOW
    MLFLOW_TRACKING_URI = var.mlflow_inter_url # http://[service-name].[namespace].svc.cluster.local:[port]
    # SLACK (TEAM CREATED)
    # SLACK_CHANNEL_ID = ""
  }
}
# EKS TEAMS' SECRETS
resource "kubernetes_secret" "eks_teams_base_secret" {
  for_each = var.eks_teams
  type     = "Opaque"

  metadata {
    name      = local.eks_k8s_base_secret_name
    namespace = var.eks_teams_kubernetes_namespaces[each.key]
  }

  data = {
    # POSTGRES
    PGUSER     = var.rds_postgres_teams_usernames[each.key]
    PGPASSWORD = var.rds_postgres_teams_passwords[each.key]
    # S3 / MWAA
    AWS_ACCESS_KEY_ID     = var.iam_teams_usernames[each.key]
    AWS_SECRET_ACCESS_KEY = var.iam_teams_passwords[each.key]
    # MLFLOW
    MLFLOW_TRACKING_USERNAME = var.mlflow_teams_usernames[each.key]
    MLFLOW_TRACKING_PASSWORD = var.mlflow_teams_passwords[each.key]
    # SLACK (TEAM CREATED)
    # SLACK_BOT_TOKEN = ""
    # SLACK_APP_TOKEN = ""
    # SLACK_SIGNING_SECRET = ""
  }
}
# EKS TEAMS' DOCKER REGISTRY
resource "kubernetes_secret" "eks_teams_docker_registry" {
  for_each = var.eks_teams
  type     = "kubernetes.io/dockerconfigjson"

  metadata {
    name      = local.eks_k8s_docker_registry_secret_name
    namespace = var.eks_teams_kubernetes_namespaces[each.key]
  }

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        # Matches to original endpoint in EKS. In MiniStack's EKS (registries.yaml), it's set to redirect to MiniStack's ECR endpoint.
        (var.ecr_aws_endpoint) = {
          username = var.ecr_aws_authorization_token_username
          password = var.ecr_aws_authorization_token_password
          auth     = var.ecr_aws_authorization_token
        }
      }
    })
  }
}
# MWAA CONNECTIONS
# > TEAMS' POSTGRES CONNECTION
resource "aws_secretsmanager_secret" "mwaa_connections_postgres_connection_id" {
  for_each = var.rds_postgres_teams
  name     = "${var.mwaa_teams_connections_prefixes[each.key]}/${local.mwaa_connections_postgres_connection_id}"
}
resource "aws_secretsmanager_secret_version" "mwaa_connections_postgres_connection_id" {
  for_each  = aws_secretsmanager_secret.mwaa_connections_postgres_connection_id
  secret_id = each.value.id

  secret_string = jsonencode({
    conn_type = "postgres",
    host      = var.rds_postgres_host[each.key],
    port      = var.rds_postgres_port[each.key],
    login     = var.rds_postgres_teams_usernames[each.key],
    password  = var.rds_postgres_teams_passwords[each.key],
    schema    = var.rds_postgres_db_name
  })

  depends_on = [aws_secretsmanager_secret.mwaa_connections_postgres_connection_id]
}
# > TEAMS' S3 CONNECTION
resource "aws_secretsmanager_secret" "mwaa_connections_s3_connection_id" {
  for_each = var.s3_teams
  name     = "${var.mwaa_teams_connections_prefixes[each.key]}/${local.mwaa_connections_s3_connection_id}"
}
resource "aws_secretsmanager_secret_version" "mwaa_connections_s3_connection_id" {
  for_each  = aws_secretsmanager_secret.mwaa_connections_s3_connection_id
  secret_id = each.value.id

  secret_string = jsonencode({
    conn_type = "aws",
    login     = var.iam_teams_usernames[each.key],
    password  = var.iam_teams_passwords[each.key],
    extra = {
      region_name = var.iam_admin_region
    }
  })

  depends_on = [aws_secretsmanager_secret.mwaa_connections_s3_connection_id]
}
# MWAA VARIABLES
# > EKS TEAMS' KUBERNETES RESOURCE NAMES
resource "aws_secretsmanager_secret" "mwaa_variables_k8s_base_config_map_name" {
  for_each = kubernetes_config_map.eks_teams_base_config_map
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_base_config_map_name}"

  depends_on = [kubernetes_config_map.eks_teams_base_config_map]
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_k8s_base_config_map_name" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_k8s_base_config_map_name
  secret_id = each.value.id

  secret_string = local.eks_k8s_base_config_map_name

  depends_on = [
    kubernetes_config_map.eks_teams_base_config_map,
    aws_secretsmanager_secret.mwaa_variables_k8s_base_config_map_name
  ]
}
resource "aws_secretsmanager_secret" "mwaa_variables_k8s_base_secret_name" {
  for_each = kubernetes_secret.eks_teams_base_secret
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_base_secret_name}"

  depends_on = [kubernetes_secret.eks_teams_base_secret]
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_k8s_base_secret_name" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_k8s_base_secret_name
  secret_id = each.value.id

  secret_string = local.eks_k8s_base_secret_name

  depends_on = [
    kubernetes_secret.eks_teams_base_secret,
    aws_secretsmanager_secret.mwaa_variables_k8s_base_secret_name
  ]
}
resource "aws_secretsmanager_secret" "mwaa_variables_k8s_docker_registry_secret_name" {
  for_each = kubernetes_secret.eks_teams_docker_registry
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_docker_registry_secret_name}"

  depends_on = [kubernetes_secret.eks_teams_docker_registry]
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_k8s_docker_registry_secret_name" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_k8s_docker_registry_secret_name
  secret_id = each.value.id

  secret_string = local.eks_k8s_docker_registry_secret_name

  depends_on = [
    kubernetes_secret.eks_teams_docker_registry,
    aws_secretsmanager_secret.mwaa_variables_k8s_docker_registry_secret_name
  ]
}
# > MWAA TEAMS' CONNECTION IDS
resource "aws_secretsmanager_secret" "mwaa_variables_postgres_connection_id" {
  for_each = aws_secretsmanager_secret.mwaa_connections_postgres_connection_id
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_postgres_connection_id}"

  depends_on = [aws_secretsmanager_secret.mwaa_connections_postgres_connection_id]
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_postgres_connection_id" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_postgres_connection_id
  secret_id = each.value.id

  secret_string = local.mwaa_connections_postgres_connection_id

  depends_on = [
    aws_secretsmanager_secret.mwaa_connections_postgres_connection_id,
    aws_secretsmanager_secret.mwaa_variables_postgres_connection_id
  ]
}
resource "aws_secretsmanager_secret" "mwaa_variables_s3_connection_id" {
  for_each = aws_secretsmanager_secret.mwaa_connections_s3_connection_id
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_s3_connection_id}"

  depends_on = [aws_secretsmanager_secret.mwaa_connections_s3_connection_id]
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_s3_connection_id" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_s3_connection_id
  secret_id = each.value.id

  secret_string = local.mwaa_connections_s3_connection_id

  depends_on = [
    aws_secretsmanager_secret.mwaa_connections_s3_connection_id,
    aws_secretsmanager_secret.mwaa_variables_s3_connection_id
  ]
}
# > MLFLOW TEAMS
resource "aws_secretsmanager_secret" "mwaa_variables_mlflow_tracking_uri" {
  for_each = var.mlflow_teams
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_mlflow_tracking_uri}"
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_mlflow_tracking_uri" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_mlflow_tracking_uri
  secret_id = each.value.id

  secret_string = var.mlflow_ingress_url

  depends_on = [aws_secretsmanager_secret.mwaa_variables_mlflow_tracking_uri]
}
resource "aws_secretsmanager_secret" "mwaa_variables_mlflow_tracking_username" {
  for_each = var.mlflow_teams
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_mlflow_tracking_username}"
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_mlflow_tracking_username" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_mlflow_tracking_username
  secret_id = each.value.id

  secret_string = var.mlflow_teams_usernames[each.key]

  depends_on = [aws_secretsmanager_secret.mwaa_variables_mlflow_tracking_username]
}
resource "aws_secretsmanager_secret" "mwaa_variables_mlflow_tracking_password" {
  for_each = var.mlflow_teams
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_mlflow_tracking_password}"
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_mlflow_tracking_password" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_mlflow_tracking_password
  secret_id = each.value.id

  secret_string = var.mlflow_teams_passwords[each.key]

  depends_on = [aws_secretsmanager_secret.mwaa_variables_mlflow_tracking_password]
}
# PLATFORM RESOURCES PROTECTION
resource "kubernetes_manifest" "platform_resources_protection" {
  for_each = var.eks_teams

  manifest = {
    apiVersion = "kyverno.io/v1"
    kind       = "Policy"
    metadata = {
      name      = "${each.key}-platform-resources-protection"
      namespace = var.eks_teams_kubernetes_namespaces[each.key]
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
                  kubernetes_secret.eks_teams_docker_registry[each.key].metadata[0].name,
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
    kubernetes_secret.eks_teams_docker_registry,
  ]
}