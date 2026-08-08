# MLFLOW
resource "helm_release" "mlflow" {
  name             = local.mlflow.host
  repository       = "https://community-charts.github.io/helm-charts"
  chart            = "mlflow"
  version          = "1.11.2" # v3.14.0 https://artifacthub.io/packages/helm/community-charts/mlflow
  namespace        = local.eks.kubernetes.mlflow.namespace
  create_namespace = true
  wait             = true
  wait_for_jobs    = true
  atomic           = true
  cleanup_on_fail  = true

  values = [file("${path.root}/helm/mlflow/values.yaml")]

  set = [
    { name = "fullnameOverride", value = local.mlflow.host },
    { name = "service.port", value = local.mlflow.port },

    { name = "backendStore.postgres.host", value = local.rds.host },
    { name = "backendStore.postgres.port", value = local.rds.port },
    { name = "backendStore.postgres.database", value = local.rds.db_name },

    { name = "extraEnvVars.MLFLOW_S3_ENDPOINT_URL", value = local.s3.network.endpoint_url },
    { name = "extraEnvVars.AWS_DEFAULT_REGION", value = local.aws.users.admin.region },
    { name = "artifactRoot.s3.bucket", value = local.s3.buckets.mlflow.name },

    { name = "auth.postgres.host", value = local.rds.host },
    { name = "auth.postgres.port", value = local.rds.port },
    { name = "auth.postgres.database", value = local.rds.db_name },
  ]

  set_sensitive = [
    { name = "backendStore.postgres.user", value = local.rds.users.mlflow.username },
    { name = "backendStore.postgres.password", value = local.rds.users.mlflow.password },

    { name = "artifactRoot.s3.awsAccessKeyId", value = local.aws.users.admin.access_key },
    { name = "artifactRoot.s3.awsSecretAccessKey", value = local.aws.users.admin.secret_key },

    { name = "auth.adminUsername", value = local.mlflow.users.admin.username },
    { name = "auth.adminPassword", value = local.mlflow.users.admin.password },
    { name = "auth.postgres.user", value = local.rds.users.mlflow.username },
    { name = "auth.postgres.password", value = local.rds.users.mlflow.password },
    { name = "flaskServerSecretKey", value = local.mlflow.flask_server_secret_key },
  ]
}
# TEAM WORKSPACES
resource "kubernetes_config_map" "create_mlflow_workspace" {
  metadata {
    name      = "create-mlflow-workspace-script"
    namespace = local.eks.kubernetes.mlflow.namespace
  }
  data = {
    (local.create_mflow_workspace_script_file_name) = file("${path.module}/${local.scripts_path_name}/${local.create_mflow_workspace_script_file_name}")
  }
  immutable = true
}
resource "kubernetes_job" "teams" {
  for_each = local.aws.users.mlflow_teams

  metadata {
    name      = "create-mlflow-workspace-${each.value}"
    namespace = local.eks.kubernetes.mlflow.namespace
  }

  spec {
    template {
      spec {
        restart_policy = "OnFailure"

        volume {
          name = kubernetes_config_map.create_mlflow_workspace.metadata[0].name
          config_map {
            name = kubernetes_config_map.create_mlflow_workspace.metadata[0].name
            default_mode = "0755" # rwx r-x r-x
          }
        }

        container {
          name  = "create-mlflow-workspace-${each.value}"
          image = "alpine:3"

          command = ["/bin/sh", "/${local.scripts_path_name}/${local.create_mflow_workspace_script_file_name}"]

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
            value = "${local.mlflow.users.admin.username}:${local.mlflow.users.admin.password}"
          }

          volume_mount {
            name       = kubernetes_config_map.create_mlflow_workspace.metadata[0].name
            mount_path = "/${local.scripts_path_name}"
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