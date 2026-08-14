# MLFLOW
resource "helm_release" "mlflow" {
  name             = var.mlflow_host
  repository       = "https://community-charts.github.io/helm-charts"
  chart            = "mlflow"
  version          = "1.11.2" # v3.14.0 https://artifacthub.io/packages/helm/community-charts/mlflow
  namespace        = var.eks_mlflow_namespace
  create_namespace = true
  wait             = true
  wait_for_jobs    = true
  atomic           = true
  cleanup_on_fail  = true

  values = [file("${path.root}/helm/mlflow/values.yaml")]

  set = [
    { name = "fullnameOverride", value = var.mlflow_host },
    { name = "extraEnvVars.SCRIPT_NAME", value = "/${var.mlflow_host}" },
    { name = "service.port", value = var.eks_traefik_http_port },
    { name = "service.containerPort", value = var.mlflow_container_port },

    { name = "backendStore.postgres.host", value = var.rds_postgres_host },
    { name = "backendStore.postgres.port", value = var.rds_postgres_port },
    { name = "backendStore.postgres.database", value = var.rds_postgres_db_name },

    { name = "extraEnvVars.MLFLOW_S3_ENDPOINT_URL", value = var.s3_egress_url },
    { name = "extraEnvVars.AWS_DEFAULT_REGION", value = var.iam_admin_region },
    { name = "artifactRoot.s3.bucket", value = var.s3_mlflow_bucket_name },

    { name = "auth.postgres.host", value = var.rds_postgres_host },
    { name = "auth.postgres.port", value = var.rds_postgres_port },
    { name = "auth.postgres.database", value = var.rds_postgres_db_name },
  ]

  set_sensitive = [
    { name = "backendStore.postgres.user", value = var.rds_postgres_mlflow_username },
    { name = "backendStore.postgres.password", value = var.rds_postgres_mlflow_password },

    { name = "artifactRoot.s3.awsAccessKeyId", value = var.iam_admin_username },
    { name = "artifactRoot.s3.awsSecretAccessKey", value = var.iam_admin_password },

    { name = "auth.adminUsername", value = var.mlflow_admin_username },
    { name = "auth.adminPassword", value = var.mlflow_admin_password },
    { name = "auth.postgres.user", value = var.rds_postgres_mlflow_username },
    { name = "auth.postgres.password", value = var.rds_postgres_mlflow_password },
    { name = "flaskServerSecretKey", value = var.mlflow_flask_server_secret_key },
  ]
}
resource "kubernetes_manifest" "mlflow_middleware" {
  manifest = {
    apiVersion = "traefik.io/v1alpha1"
    kind       = "Middleware"
    metadata = {
      name      = "MLFLOW_MIDDLEWARE"
      namespace = var.eks_mlflow_namespace
    }
    spec = {
      stripPrefix = {
        prefixes = ["/${var.mlflow_host}"]
      }
    }
  }

  depends_on = [helm_release.mlflow]
}
resource "kubernetes_manifest" "mlflow_ingress_route" {
  manifest = {
    apiVersion = "traefik.io/v1alpha1"
    kind       = "IngressRoute"
    metadata = {
      name      = "MLFLOW_INGRESS_ROUTE"
      namespace = var.eks_mlflow_namespace
    }
    spec = {
      entryPoints = ["web", "websecure"] # http 80 / https 443
      routes = [
        {
          match = "PathPrefix(`/${var.mlflow_host}`)"
          kind  = "Rule"
          middlewares = [
            {
              name      = kubernetes_manifest.mlflow_middleware.manifest.metadata.name
              namespace = var.eks_mlflow_namespace
            }
          ]
          services = [
            {
              name = var.mlflow_host
              port = var.eks_traefik_http_port
            }
          ]
        }
      ]
    }
  }

  depends_on = [
    helm_release.mlflow,
    kubernetes_manifest.mlflow_middleware,
  ]
}
# MLFLOW TEAMS' WORKSPACES
resource "kubernetes_config_map" "create_mlflow_workspace" {
  metadata {
    name      = "CREATE_MLFLOW_WORKSPACE_SCRIPT"
    namespace = var.eks_mlflow_namespace
  }
  data = {
    (local.create_mlflow_workspace_script_file_name) = file("${path.module}/${local.create_mlflow_workspace_script_file_relative_path}")
  }
  immutable = true
}
resource "kubernetes_job" "mlflow_teams" {
  for_each = var.mlflow_teams

  metadata {
    name      = "CREATE_MLFLOW_WORKSPACE_FOR_${each.key}"
    namespace = var.eks_mlflow_namespace
  }

  spec {
    template {
      spec {
        restart_policy = "OnFailure"

        volume {
          name = kubernetes_config_map.create_mlflow_workspace.metadata[0].name
          config_map {
            name         = kubernetes_config_map.create_mlflow_workspace.metadata[0].name
            default_mode = "0755" # rwx r-x r-x
          }
        }

        container {
          name  = "CREATE_MLFLOW_WORKSPACE_FOR_${each.key}"
          image = "alpine:3"

          command = ["/bin/sh", "/${local.create_mlflow_workspace_script_file_relative_path}"]

          env {
            name  = "MLFLOW_INTERNAL_URL"
            value = local.mlflow_url.internal
          }
          env {
            name  = "WORKSPACE_NAME"
            value = each.key
          }
          env {
            name  = "USERNAME"
            value = each.key
          }
          env {
            name  = "PASSWORD"
            value = each.key # Team can change it themselves (PATCH /api/2.0/mlflow/users/update-password)
          }
          env {
            name  = "ADMIN"
            value = "${var.mlflow_admin_username}:${var.mlflow_admin_password}"
          }

          volume_mount {
            name       = kubernetes_config_map.create_mlflow_workspace.metadata[0].name
            mount_path = "/${local.scripts_relative_path}"
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