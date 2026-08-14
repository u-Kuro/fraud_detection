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
    { name = "extraEnvVars.SCRIPT_NAME", value = "/${local.mlflow.host}" },
    { name = "service.port", value = local.system_ports.http },
    { name = "service.containerPort", value = local.mlflow.port.container },

    { name = "backendStore.postgres.host", value = local.rds.postgres.host },
    { name = "backendStore.postgres.port", value = local.rds.postgres.port },
    { name = "backendStore.postgres.database", value = local.rds.postgres.db_name },

    { name = "extraEnvVars.MLFLOW_S3_ENDPOINT_URL", value = local.s3.url.egress },
    { name = "extraEnvVars.AWS_DEFAULT_REGION", value = local.iam.users.admin.region },
    { name = "artifactRoot.s3.bucket", value = local.s3.buckets.mlflow.name },

    { name = "auth.postgres.host", value = local.rds.postgres.host },
    { name = "auth.postgres.port", value = local.rds.postgres.port },
    { name = "auth.postgres.database", value = local.rds.postgres.db_name },
  ]

  set_sensitive = [
    { name = "backendStore.postgres.user", value = local.rds.postgres.users.mlflow.username },
    { name = "backendStore.postgres.password", value = local.rds.postgres.users.mlflow.password },

    { name = "artifactRoot.s3.awsAccessKeyId", value = local.iam.users.admin.username },
    { name = "artifactRoot.s3.awsSecretAccessKey", value = local.iam.users.admin.password },

    { name = "auth.adminUsername", value = local.mlflow.users.admin.username },
    { name = "auth.adminPassword", value = local.mlflow.users.admin.password },
    { name = "auth.postgres.user", value = local.rds.postgres.users.mlflow.username },
    { name = "auth.postgres.password", value = local.rds.postgres.users.mlflow.password },
    { name = "flaskServerSecretKey", value = local.mlflow.flask_server_secret_key },
  ]
}
resource "kubernetes_manifest" "mlflow_middleware" {
  manifest = {
    apiVersion = "traefik.io/v1alpha1"
    kind       = "Middleware"
    metadata = {
      name      = "MLFLOW_MIDDLEWARE"
      namespace = local.eks.kubernetes.mlflow.namespace
    }
    spec = {
      stripPrefix = {
        prefixes = ["/${local.mlflow.host}"]
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
      namespace = local.eks.kubernetes.mlflow.namespace
    }
    spec = {
      entryPoints = ["web", "websecure"] # http 80 / https 443
      routes = [
        {
          match = "PathPrefix(`/${local.mlflow.host}`)"
          kind  = "Rule"
          middlewares = [
            {
              name      = kubernetes_manifest.mlflow_middleware.manifest.metadata.name
              namespace = local.eks.kubernetes.mlflow.namespace
            }
          ]
          services = [
            {
              name = local.mlflow.host
              port = local.system_ports.http
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
    namespace = local.eks.kubernetes.mlflow.namespace
  }
  data = {
    (local.create_mlflow_workspace_script_file_name) = file("${path.module}/${local.create_mlflow_workspace_script_file_relative_path}")
  }
  immutable = true
}
resource "kubernetes_job" "mlflow_teams" {
  for_each = local.mlflow.users.teams

  metadata {
    name      = "CREATE_MLFLOW_WORKSPACE_FOR_${each.key}"
    namespace = local.eks.kubernetes.mlflow.namespace
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
            value = "${local.mlflow.users.admin.username}:${local.mlflow.users.admin.password}"
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