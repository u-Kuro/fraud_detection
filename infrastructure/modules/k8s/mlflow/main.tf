# Create MLflow release
resource "helm_release" "mlflow" {
  name             = var.mlflow_host
  repository       = "https://community-charts.github.io/helm-charts"
  chart            = "mlflow"
  version          = "1.11.5" # v3.15.1 https://artifacthub.io/packages/helm/community-charts/mlflow/1.11.5
  namespace        = var.eks_mlflow_namespace
  create_namespace = true
  wait             = true
  wait_for_jobs    = true
  timeout          = 600

  values = [file("${path.module}/configurations/values.yaml")]

  set = [
    { name = "image.tag", value = "3.15.2-alpine" },

    { name = "fullnameOverride", value = var.mlflow_host },
    { name = "service.port", value = var.mlflow_port },

    { name = "backendStore.postgres.host", value = var.rds_postgres_host },
    { name = "backendStore.postgres.port", value = var.rds_postgres_port },
    { name = "backendStore.postgres.database", value = var.rds_postgres_db_name },

    { name = "extraEnvVars.MLFLOW_S3_ENDPOINT_URL", value = var.s3_url },
    { name = "extraEnvVars.AWS_DEFAULT_REGION", value = var.iam_admin_region },
    { name = "artifactRoot.s3.bucket", value = var.s3_mlflow_bucket_name },

    { name = "auth.postgres.host", value = var.rds_postgres_host },
    { name = "auth.postgres.port", value = var.rds_postgres_port },
    { name = "auth.postgres.database", value = var.rds_postgres_db_name },
  ]

  set_list = [
    {
      name = "serverAllowedHosts",
      value = [
        var.mlflow_host,
        local.mlflow_inter_host,
        local.mlflow_subdomain,
        local.mlflow_subdomain_from_host
      ]
    },
  ]

  set_sensitive = [
    { name = "backendStore.postgres.user", value = var.rds_postgres_mlflow_username },
    { name = "backendStore.postgres.password", value = var.rds_postgres_mlflow_password },

    { name = "artifactRoot.s3.awsAccessKeyId", value = var.iam_admin_access_key },
    { name = "artifactRoot.s3.awsSecretAccessKey", value = var.iam_admin_secret_key },

    { name = "auth.adminUsername", value = var.mlflow_admin_username },
    { name = "auth.adminPassword", value = var.mlflow_admin_password },
    { name = "auth.postgres.user", value = var.rds_postgres_mlflow_username },
    { name = "auth.postgres.password", value = var.rds_postgres_mlflow_password },
    { name = "flaskServerSecretKey", value = var.mlflow_flask_server_secret_key },
  ]
}
# Adds ingress route in Traefik for MLflow subdomain
resource "kubectl_manifest" "ingress_route" {
  yaml_body = yamlencode({
    apiVersion = "traefik.io/v1alpha1"
    kind       = "IngressRoute"
    metadata = {
      name      = "${var.mlflow_host}-ingress-route"
      namespace = helm_release.mlflow.namespace
    }
    spec = {
      entryPoints = ["web", "websecure"] # http 80 / https 443
      routes = [
        {
          match = "Host(`${local.mlflow_subdomain}`)"
          kind  = "Rule"
          services = [
            {
              name = var.mlflow_host
              port = var.mlflow_port
            }
          ]
        },
        {
          match = "Host(`${local.mlflow_subdomain_from_host}`)"
          kind  = "Rule"
          services = [
            {
              name = var.mlflow_host
              port = var.mlflow_port
            }
          ]
        }
      ]
    }
  })
}
# Create script in cluster for creating MLflow workspace
resource "kubernetes_config_map_v1" "create_mlflow_workspace" {
  metadata {
    name      = local.create_mlflow_workspace_script_file_resource_name
    namespace = helm_release.mlflow.namespace
  }
  data = {
    (local.create_mlflow_workspace_script_file_name) = file("${path.module}/${local.create_mlflow_workspace_script_file_relative_path}")
  }
  immutable = true
}
# Runs the job to create MLflow workspaces for each team
resource "kubernetes_job_v1" "teams" {
  for_each            = var.mlflow_teams
  wait_for_completion = true
  timeouts {
    create = "10m"
    update = "10m"
    delete = "10m"
  }

  metadata {
    name      = "create-mlflow-workspace-for-${each.key}"
    namespace = helm_release.mlflow.namespace
  }

  spec {
    parallelism                = 1
    ttl_seconds_after_finished = 300
    template {
      metadata {}
      spec {
        restart_policy = "OnFailure"

        volume {
          name = local.create_mlflow_workspace_script_file_resource_name
          config_map {
            name         = local.create_mlflow_workspace_script_file_resource_name
            default_mode = "0755" # rwx r-x r-x
          }
        }

        container {
          name  = "create-mlflow-workspace-for-${each.key}"
          image = "alpine:3.24.1"

          command = ["/bin/sh", "/${local.create_mlflow_workspace_script_file_relative_path}"]

          env {
            name  = "MLFLOW_URL"
            value = local.mlflow_intra_url
          }
          env {
            name  = "WORKSPACE_NAME"
            value = local.mlflow_teams_workspace_names[each.key]
          }
          env {
            name  = "ROLE_NAME"
            value = local.mlflow_teams_role_names[each.key]
          }
          env {
            name  = "USERNAME"
            value = local.mlflow_teams_usernames[each.key]
          }
          env {
            name  = "PASSWORD"
            value = local.mlflow_teams_passwords[each.key] # Team can change it themselves (PATCH /api/2.0/mlflow/users/update-password)
          }
          env {
            name  = "ADMIN"
            value = "${var.mlflow_admin_username}:${var.mlflow_admin_password}"
          }

          volume_mount {
            name       = local.create_mlflow_workspace_script_file_resource_name
            mount_path = "/${local.scripts_relative_path}"
          }
        }
      }
    }
  }

  depends_on = [
    kubernetes_config_map_v1.create_mlflow_workspace # Needs the script to create mlflow workspace
  ]
}