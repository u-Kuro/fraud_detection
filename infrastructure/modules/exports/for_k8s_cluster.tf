# Initialization
# /teams-namespaces
resource "kubernetes_namespace_v1" "eks_teams" {
  for_each = var.eks_teams
  metadata {
    name = var.eks_teams_namespaces[each.key]
  }
}
# ConfigMap
# /base-for-teams-namespaces
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

  depends_on = [
    kubernetes_namespace_v1.eks_teams
  ]
}
# Secrets
# /base-for-teams-namespaces
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

  depends_on = [
    kubernetes_namespace_v1.eks_teams
  ]
}
# /docker-registry-for-teams-namespaces
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

  depends_on = [
    kubernetes_namespace_v1.eks_teams
  ]
}
# Policies
# /config-maps
resource "kubectl_manifest" "platform_configmap_protection" {
  for_each = var.eks_teams

  yaml_body = yamlencode({
    apiVersion = "policies.kyverno.io/v1"
    kind       = "NamespacedValidatingPolicy"
    metadata = {
      name      = "${each.key}-platform-configmap-protection"
      namespace = var.eks_teams_namespaces[each.key]
    }
    spec = {
      validationActions = ["Deny"]
      matchConstraints = {
        resourceRules = [{
          apiGroups   = [""]
          apiVersions = ["v1"]
          operations  = ["UPDATE", "DELETE"]
          resources   = ["configmaps"]
        }]
      }
      matchConditions = [
        {
          name       = "is-platform-configmap"
          expression = "(object != null ? object : oldObject).metadata.name == '${local.eks_k8s_base_config_map_name}'"
        },
        {
          name       = "not-cluster-admin"
          expression = "!('system:masters' in request.userInfo.groups)"
        }
      ]
      validations = [{
        message    = "Platform-managed ConfigMap cannot be modified."
        expression = "false"
      }]
    }
  })

  depends_on = [
    kubernetes_namespace_v1.eks_teams,
    kubernetes_config_map_v1.eks_teams_base_config_map,
  ]
}
# /secrets
resource "kubectl_manifest" "platform_secret_protection" {
  for_each = var.eks_teams

  yaml_body = yamlencode({
    apiVersion = "policies.kyverno.io/v1"
    kind       = "NamespacedValidatingPolicy"
    metadata = {
      name      = "${each.key}-platform-secret-protection"
      namespace = var.eks_teams_namespaces[each.key]
    }
    spec = {
      validationActions = ["Deny"]
      matchConstraints = {
        resourceRules = [{
          apiGroups   = [""]
          apiVersions = ["v1"]
          operations  = ["UPDATE", "DELETE"]
          resources   = ["secrets"]
        }]
      }
      matchConditions = [
        {
          name       = "is-platform-secret"
          expression = "(object != null ? object : oldObject).metadata.name in ['${local.eks_k8s_base_secret_name}', '${local.eks_k8s_docker_registry_secret_name}']"
        },
        {
          name       = "not-cluster-admin"
          expression = "!('system:masters' in request.userInfo.groups)"
        }
      ]
      validations = [{
        message    = "Platform-managed Secret cannot be modified."
        expression = "false"
      }]
    }
  })

  depends_on = [
    kubernetes_namespace_v1.eks_teams,
    kubernetes_secret_v1.eks_teams_base_secret,
    kubernetes_secret_v1.eks_teams_docker_registry,
  ]
}
