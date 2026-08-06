# TODO - 06/08/2026 - Continue here....
# some random password like mlflow_flask_server_secret_key may be better in tfvars so its not changing and is sensitive=true
# check if its better if we can create a list/dict in tfvars instead for team password e.g. postgres team passwords (multiple)
resource "random_password" "mlflow_flask_server_secret_key" {
  length  = 64
  special = false
}
resource "helm_release" "mlflow" {
  name              = var.mlflow_host
  repository        = "https://community-charts.github.io/helm-charts"
  chart             = "mlflow"
  version           = "1.11.2" # v3.14.0 https://artifacthub.io/packages/helm/community-charts/mlflow
  namespace         = "default"
  create_namespace  = true
  wait              = true
  wait_for_jobs     = true
  atomic            = true
  cleanup_on_fail   = true

  values = [file("${path.root}/helm/mlflow/values.yaml")]

  set = [
    { name = "fullnameOverride",                    value = var.mlflow_host },
    { name = "service.port",                        value = var.mlflow_port },

    { name = "backendStore.postgres.host",          value = var.rds_db_address },
    { name = "backendStore.postgres.port",          value = var.rds_db_port },
    { name = "backendStore.postgres.database",      value = var.rds_db_name },

    { name = "extraEnvVars.MLFLOW_S3_ENDPOINT_URL", value = var.s3_internal_endpoint_url },
    { name = "extraEnvVars.AWS_DEFAULT_REGION",     value = var.s3_mlflow_bucket_aws_region },
    { name = "artifactRoot.s3.bucket",              value = var.s3_mlflow_bucket },

    { name = "auth.postgres.host",     value = var.rds_db_address },
    { name = "auth.postgres.port",     value = var.rds_db_port },
    { name = "auth.postgres.database", value = var.rds_db_name },
  ]

  set_sensitive = [
    { name = "backendStore.postgres.user",             value = var.mlflow_db_username },
    { name = "backendStore.postgres.password",         value = var.mlflow_db_password },

    { name = "artifactRoot.s3.awsAccessKeyId",         value = var.admin.access_key },
    { name = "artifactRoot.s3.awsSecretAccessKey",     value = var.admin.secret_key },

    { name = "auth.adminUsername",      value = var.mlflow_admin_username },
    { name = "auth.adminPassword",      value = var.mlflow_admin_password },
    { name = "auth.postgres.user",      value = var.mlflow_db_username },
    { name = "auth.postgres.password",  value = var.mlflow_db_password },
    { name = "flaskServerSecretKey",    value = random_password.mlflow_flask_server_secret_key.result },
  ]

  depends_on = [random_password.mlflow_flask_server_secret_key]
}

locals {
  mlflow_tracking_uri = "http://${var.mlflow_host}:${var.mlflow_port}"
}
resource "random_password" "team_mlflow_credentials" {
  for_each = var.mlflow_teams
  length  = 24
}
resource "kubernetes_job" "mlflow_create_workspaces" {
  for_each = random_password.team_mlflow_credentials

  metadata {
    namespace = "default"
  }
  spec {
    template {
      spec {
        restart_policy = "OnFailure"
        container {
          name  = "create_mlflow_workspace_${each.key}"
          image = "curlimages/curl:latest"
          command = [
            "sh", "-c",
            <<-EOT
              # Create user per team
              curl -X POST ${local.mlflow_tracking_uri}/api/2.0/mlflow/users/create \
                -u "${var.mlflow_admin_username}:${var.mlflow_admin_password}" \
                -H "Content-Type: application/json" \
                -d '{"username": "${each.key}", "password": "${each.value.result}"}'

              # Create workspace per team
              curl -X POST ${local.mlflow_tracking_uri}/api/3.0/mlflow/workspaces \
                -u "${var.mlflow_admin_username}:${var.mlflow_admin_password}" \
                -H "Content-Type: application/json" \
                -d '{"name": "${each.key}_workspace"}'

              # Give team edit permission to their workspace
              curl -X POST ${local.mlflow_tracking_uri}/api/3.0/mlflow/workspaces/each.key/permissions \
                -u "${var.mlflow_admin_username}:${var.mlflow_admin_password}" \
                -H "Content-Type: application/json" \
                -d '{"username": "${each.key}", "permission": "EDIT"}'
            EOT
          ]
        }
      }
    }
  }

  depends_on = [
    helm_release.mlflow,
  ]
}