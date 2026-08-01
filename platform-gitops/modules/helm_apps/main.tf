resource "helm_release" "mlflow" {
  name             = var.mlflow_host
  repository       = "https://community-charts.github.io/helm-charts"
  chart            = "mlflow"
  namespace        = "default"
  create_namespace = true
  timeout          = 300
  wait             = true

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
  ]

  set_sensitive = [
    { name = "backendStore.postgres.user",             value = var.mlflow_db_username },
    { name = "backendStore.postgres.password",         value = var.mlflow_db_password },

    { name = "artifactRoot.s3.awsAccessKeyId",         value = var.aws_access_key },
    { name = "artifactRoot.s3.awsSecretAccessKey",     value = var.aws_secret_key },
  ]
}

# # ── Post-deploy: create one MLflow workspace per team that has MLflow access ──
# locals {
#   mlflow_tracking_uri = "http://${var.mlflow_host}:${var.mlflow_port}"
# }
# resource "random_password" "team_mlflow_credentials" {
#   for_each = var.mlflow_workspace_names
#   length  = 24
# }
# resource "kubernetes_job" "mlflow_create_workspaces" {
#   for_each = random_password.team_mlflow_credentials
#
#   metadata {
#     name      = "mlflow-create-${each.key}-workspace"
#     namespace = "default"
#   }
#   spec {
#     template {
#       spec {
#         restart_policy = "OnFailure"
#         container {
#           name  = "mlflow-workspace-init"
#           image = "curlimages/curl:latest"
#           env {
#             name  = "MLFLOW_TRACKING_USERNAME"
#             value = each.key
#           }
#           env {
#             name  = "MLFLOW_TRACKING_PASSWORD"
#             value = each.value.result
#           }
#           command = [
#             "sh", "-c",
#             <<-EOT
#               curl -sf -X POST \
#                 -u "$MLFLOW_TRACKING_USERNAME:$MLFLOW_TRACKING_PASSWORD" \
#                 "${local.mlflow_tracking_uri}/api/2.0/mlflow/workspaces/create" \
#                 -H "Content-Type: application/json" \
#                 -d '{"name":"${each.key}-workspace"}'
#             EOT
#           ]
#         }
#       }
#     }
#   }
#
#   depends_on = [helm_release.mlflow]
# }