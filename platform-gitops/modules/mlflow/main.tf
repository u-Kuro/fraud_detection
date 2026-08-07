# MLFLOW
locals {
  namespace = "mlflow"
}
resource "helm_release" "mlflow" {
  name             = var.mlflow.host
  repository       = "https://community-charts.github.io/helm-charts"
  chart            = "mlflow"
  version          = "1.11.2" # v3.14.0 https://artifacthub.io/packages/helm/community-charts/mlflow
  namespace        = local.namespace
  create_namespace = true
  wait             = true
  wait_for_jobs    = true
  atomic           = true
  cleanup_on_fail  = true

  values = [file("${path.root}/helm/mlflow/values.yaml")]

  set = [
    { name = "fullnameOverride", value = var.mlflow.host },
    { name = "service.port", value = var.mlflow.port },

    { name = "backendStore.postgres.host", value = var.rds.host },
    { name = "backendStore.postgres.port", value = var.rds.port },
    { name = "backendStore.postgres.database", value = var.rds.db_name },

    { name = "extraEnvVars.MLFLOW_S3_ENDPOINT_URL", value = var.s3.network.endpoint_url },
    { name = "extraEnvVars.AWS_DEFAULT_REGION", value = var.aws.users.admin.region },
    { name = "artifactRoot.s3.bucket", value = var.s3.buckets.mlflow.name },

    { name = "auth.postgres.host", value = var.rds.host },
    { name = "auth.postgres.port", value = var.rds.port },
    { name = "auth.postgres.database", value = var.rds.db_name },
  ]

  set_sensitive = [
    { name = "backendStore.postgres.user", value = var.rds.users.mlflow.username },
    { name = "backendStore.postgres.password", value = var.rds.users.mlflow.password },

    { name = "artifactRoot.s3.awsAccessKeyId", value = var.aws.users.admin.access_key },
    { name = "artifactRoot.s3.awsSecretAccessKey", value = var.aws.users.admin.secret_key },

    { name = "auth.adminUsername", value = var.mlflow.users.admin.username },
    { name = "auth.adminPassword", value = var.mlflow.users.admin.password },
    { name = "auth.postgres.user", value = var.rds.users.mlflow.username },
    { name = "auth.postgres.password", value = var.rds.users.mlflow.password },
    { name = "flaskServerSecretKey", value = var.mlflow.flask_server_secret_key },
  ]
}
# TEAM WORKSPACES
locals {
  scripts_directory_path                  = "scripts"
  create_mflow_workspace_script_file_name = "create_mlflow_workspace.sh"
}
resource "kubernetes_config_map" "create_mlflow_workspace" {
  metadata {
    name      = "create-mlflow-workspace-script"
    namespace = local.namespace
  }
  data = {
    (local.create_mflow_workspace_script_file_name) = file("${path.module}/${local.scripts_directory_path}/${local.create_mflow_workspace_script_file_name}")
  }
  immutable = true
}
locals {
  create_mflow_workspace_script_volume_name = "scripts"
  mlflow_tracking_uri                       = "http://${var.mlflow.host}:${var.mlflow.port}"
}
resource "kubernetes_job" "teams" {
  for_each = var.aws.users.mlflow_teams

  metadata {
    name      = "create-mlflow-workspace-${each.value}"
    namespace = local.namespace
  }

  spec {
    template {
      spec {
        restart_policy = "OnFailure"

        volume {
          name = local.create_mflow_workspace_script_volume_name
          config_map {
            name = kubernetes_config_map.create_mlflow_workspace.metadata[0].name
          }
        }

        container {
          name  = "create-mlflow-workspace-${each.value}"
          image = "alpine:3"

          command = ["/bin/sh", "/${local.scripts_directory_path}/${local.create_mflow_workspace_script_file_name}"]

          env {
            name  = "MLFLOW_TRACKING_URI"
            value = local.mlflow_tracking_uri
          }
          env {
            name  = "TEAM"
            value = each.value
          }
          env {
            name  = "PASSWORD"
            value = each.value # Team can change it themselves (PATCH /api/2.0/mlflow/users/update-password)
          }
          env {
            name  = "ADMIN"
            value = "${var.mlflow.users.admin.username}:${var.mlflow.users.admin.password}"
          }

          volume_mount {
            name       = local.create_mflow_workspace_script_volume_name
            mount_path = "/${local.scripts_directory_path}"
          }
        }
      }
    }
  }

  depends_on = [
    helm_release.mlflow,
    kubernetes_config_map.create_mlflow_workspace
  ]
}