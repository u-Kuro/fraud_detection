# What else are essential

# DAGs (secretsmanager) - DONE CHECKING
# 1) postgres connection - ok
# 2) Slack connection + slack channel id - user created
# 3) mlflow url and credentials - ok
# 4) kubernetes connection - ok
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

# Create base kubernetes config map for each teams' namespace
resource "kubernetes_config_map_v1" "eks_teams_base_config_map" {
  for_each = var.eks_teams

  metadata {
    name      = local.eks_k8s_base_config_map_name
    namespace = var.eks_teams_namespaces[each.key]
  }

  data = {
    # Postgres
    PGHOST     = var.rds_postgres_host
    PGPORT     = var.rds_postgres_port
    PGDATABASE = var.rds_postgres_db_name
    # AWS
    AWS_DEFAULT_REGION = var.iam_admin_region
    # S3
    AWS_ENDPOINT_URL_S3 = var.s3_url
    S3_BUCKET_NAME      = var.s3_teams_bucket_names[each.key]
    # MWAA
    AWS_ENDPOINT_URL_MWAA = var.mwaa_url
    MWAA_ENVIRONMENT_NAME = var.mwaa_teams_environment_names[each.key] # Not Fixed
    # MLflow
    MLFLOW_TRACKING_URI = var.mlflow_inter_url # http://[service-name].[namespace].svc.cluster.local:[port]
    # Slack (team created)
    # SLACK_CHANNEL_ID = ""
  }
}
# Create base kubernetes secret for each teams' namespace
resource "kubernetes_secret_v1" "eks_teams_base_secret" {
  for_each = var.eks_teams
  type     = "Opaque"

  metadata {
    name      = local.eks_k8s_base_secret_name
    namespace = var.eks_teams_namespaces[each.key]
  }

  data = {
    # Postgres
    PGUSER     = var.rds_postgres_teams_usernames[each.key]
    PGPASSWORD = var.rds_postgres_teams_passwords[each.key]
    # AWS
    AWS_ACCESS_KEY_ID     = var.iam_teams_usernames[each.key]
    AWS_SECRET_ACCESS_KEY = var.iam_teams_passwords[each.key]
    # MLflow
    MLFLOW_TRACKING_USERNAME = var.mlflow_teams_usernames[each.key]
    MLFLOW_TRACKING_PASSWORD = var.mlflow_teams_passwords[each.key]
    # Slack (team created)
    # SLACK_BOT_TOKEN = ""
    # SLACK_APP_TOKEN = ""
    # SLACK_SIGNING_SECRET = ""
  }
}
# Create kubernetes docker registry for each teams' namespace
resource "kubernetes_secret_v1" "eks_teams_docker_registry" {
  for_each = var.eks_teams
  type     = "kubernetes.io/dockerconfigjson"

  metadata {
    name      = local.eks_k8s_docker_registry_secret_name
    namespace = var.eks_teams_namespaces[each.key]
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
# Create Kubernetes connection for each teams' MWAA
resource "aws_secretsmanager_secret" "mwaa_connections_k8s_connection_id" {
  for_each = var.mwaa_teams
  name     = "${var.mwaa_teams_connections_prefixes[each.key]}/${local.mwaa_connections_k8s_connection_id}"
}
resource "aws_secretsmanager_secret_version" "mwaa_connections_k8s_connection_id" {
  for_each  = aws_secretsmanager_secret.mwaa_connections_k8s_connection_id
  secret_id = each.value.id

  secret_string = jsonencode({
    conn_type = "kubernetes",
    extra = {
      kube_config_path = var.mwaa_teams_kubeconfig_file_paths[each.key] # /opt/airflow/kubeconfig.yaml
      namespace        = var.eks_teams_namespaces[each.key]
      in_cluster       = false
    }
  })

  depends_on = [aws_secretsmanager_secret.mwaa_connections_k8s_connection_id]
}
# Create Postgres connection for each teams' MWAA
resource "aws_secretsmanager_secret" "mwaa_connections_postgres_connection_id" {
  for_each = var.rds_postgres_teams
  name     = "${var.mwaa_teams_connections_prefixes[each.key]}/${local.mwaa_connections_postgres_connection_id}"
}
resource "aws_secretsmanager_secret_version" "mwaa_connections_postgres_connection_id" {
  for_each  = aws_secretsmanager_secret.mwaa_connections_postgres_connection_id
  secret_id = each.value.id

  secret_string = jsonencode({
    conn_type = "postgres",
    host      = var.rds_postgres_host,
    port      = var.rds_postgres_port,
    login     = var.rds_postgres_teams_usernames[each.key],
    password  = var.rds_postgres_teams_passwords[each.key],
    schema    = var.rds_postgres_db_name
  })

  depends_on = [aws_secretsmanager_secret.mwaa_connections_postgres_connection_id]
}
# Create S3 connection for each teams' MWAA
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
# Create name variable of the base Kubernetes config map for each team
resource "aws_secretsmanager_secret" "mwaa_variables_k8s_base_config_map_name" {
  for_each = kubernetes_config_map_v1.eks_teams_base_config_map
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_base_config_map_name}"
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_k8s_base_config_map_name" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_k8s_base_config_map_name
  secret_id = each.value.id

  secret_string = local.eks_k8s_base_config_map_name

  depends_on = [
    kubernetes_config_map_v1.eks_teams_base_config_map,
    aws_secretsmanager_secret.mwaa_variables_k8s_base_config_map_name
  ]
}
# Create name variable of the base Kubernetes secret for each team
resource "aws_secretsmanager_secret" "mwaa_variables_k8s_base_secret_name" {
  for_each = kubernetes_secret_v1.eks_teams_base_secret
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_base_secret_name}"
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_k8s_base_secret_name" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_k8s_base_secret_name
  secret_id = each.value.id

  secret_string = local.eks_k8s_base_secret_name

  depends_on = [
    kubernetes_secret_v1.eks_teams_base_secret,
    aws_secretsmanager_secret.mwaa_variables_k8s_base_secret_name
  ]
}
# Create variable name of Kubernetes docker registry for each team
resource "aws_secretsmanager_secret" "mwaa_variables_k8s_docker_registry_secret_name" {
  for_each = kubernetes_secret_v1.eks_teams_docker_registry
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_docker_registry_secret_name}"
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_k8s_docker_registry_secret_name" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_k8s_docker_registry_secret_name
  secret_id = each.value.id

  secret_string = local.eks_k8s_docker_registry_secret_name

  depends_on = [
    kubernetes_secret_v1.eks_teams_docker_registry,
    aws_secretsmanager_secret.mwaa_variables_k8s_docker_registry_secret_name
  ]
}
# Create ID variable for the Kubernetes connection for each team
resource "aws_secretsmanager_secret" "mwaa_variables_k8s_connection_id" {
  for_each = aws_secretsmanager_secret.mwaa_connections_k8s_connection_id
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_connection_id}"

  depends_on = [aws_secretsmanager_secret.mwaa_connections_k8s_connection_id]
}
resource "aws_secretsmanager_secret_version" "mwaa_variables_k8s_connection_id" {
  for_each  = aws_secretsmanager_secret.mwaa_variables_k8s_connection_id
  secret_id = each.value.id

  secret_string = local.mwaa_connections_k8s_connection_id

  depends_on = [
    aws_secretsmanager_secret.mwaa_connections_k8s_connection_id,
    aws_secretsmanager_secret.mwaa_variables_k8s_connection_id
  ]
}
# Create ID variable for the Postgres connection for each team
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
# Create ID variable for the S3 connection for each team
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
# Create URL variable of MLflow for each team
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
# Create username variable for each teams' MLflow account
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
# Create password variable for each teams' MLflow account
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
# Set Kubernetes policy to deny teams in editing infrastructure resources
resource "kubectl_manifest" "platform_resources_protection" {
  for_each = var.eks_teams

  yaml_body = yamlencode({
    apiVersion = "kyverno.io/v1"
    kind       = "Policy"
    metadata = {
      name      = "${each.key}-platform-resources-protection"
      namespace = var.eks_teams_namespaces[each.key]
    }
    spec = {
      rules = [
        {
          name = "platform-config-map-protection"
          match = {
            any = [{
              resources = {
                kinds      = ["ConfigMap"]
                names      = [local.eks_k8s_base_config_map_name]
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
                  local.eks_k8s_base_secret_name,
                  local.eks_k8s_docker_registry_secret_name,
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
  })

  depends_on = [
    kubernetes_config_map_v1.eks_teams_base_config_map,
    kubernetes_secret_v1.eks_teams_base_secret,
    kubernetes_secret_v1.eks_teams_docker_registry,
  ]
}