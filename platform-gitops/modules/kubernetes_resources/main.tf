# ─────────────────────────────────────────────────────────────────────────────
# Team Namespaces
# ─────────────────────────────────────────────────────────────────────────────
resource "kubernetes_namespace" "team" {
  for_each = var.teams
  metadata {
    name   = each.value.namespace
    labels = { team = each.key }
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# Service Accounts — annotated with IRSA role ARN so pods can call AWS APIs.
# The aws_iam_oidc module trust policy is pinned to
# "system:serviceaccount:<namespace>:<team>-sa", so this name must match.
# ─────────────────────────────────────────────────────────────────────────────
resource "kubernetes_service_account" "team" {
  for_each = var.teams
  metadata {
    name      = "${each.key}-sa"
    namespace = kubernetes_namespace.team[each.key].metadata[0].name
    annotations = {
      "eks.amazonaws.com/role-arn" = var.team_role_arns[each.key]
    }
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# Team RBAC Role — scoped strictly to the team's own namespace.
# Teams can manage their own Pods, Deployments, Secrets, and ConfigMaps
# but cannot touch any resource outside their namespace.
# ─────────────────────────────────────────────────────────────────────────────
resource "kubernetes_role" "team" {
  for_each = var.teams
  metadata {
    name      = "${each.key}-role"
    namespace = kubernetes_namespace.team[each.key].metadata[0].name
  }

  rule {
    api_groups = [""]
    resources  = ["pods", "pods/log", "pods/exec", "pods/status"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
  rule {
    api_groups = ["apps"]
    resources  = ["deployments", "replicasets", "statefulsets"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
  rule {
    api_groups = [""]
    resources  = ["secrets"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
  rule {
    api_groups = [""]
    resources  = ["configmaps"]
    verbs      = ["get", "list", "watch", "create", "update", "patch", "delete"]
  }
}

resource "kubernetes_role_binding" "team" {
  for_each = var.teams
  metadata {
    name      = "${each.key}-role-binding"
    namespace = kubernetes_namespace.team[each.key].metadata[0].name
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.team[each.key].metadata[0].name
  }
  subject {
    kind      = "Group"
    name      = "${each.key}-group"
    api_group = "rbac.authorization.k8s.io"
  }
  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.team[each.key].metadata[0].name
    namespace = kubernetes_namespace.team[each.key].metadata[0].name
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# Shared ConfigMap — lives in the default namespace.
# Contains platform-wide non-sensitive endpoints that multiple teams need.
# ─────────────────────────────────────────────────────────────────────────────
resource "kubernetes_config_map" "shared" {
  metadata {
    name      = "shared-platform-config"
    namespace = "default"
  }
  data = {
    PGHOST              = var.rds_host
    PGPORT              = tostring(var.rds_port)
    PGDATABASE          = var.rds_db_name
    MLFLOW_TRACKING_URI = var.mlflow_tracking_uri
    MWAA_WEBSERVER_URL  = var.mwaa_webserver_url
    AWS_DEFAULT_REGION  = var.aws_region
    S3_ENDPOINT_URL     = var.s3_endpoint_url
  }
}

# A Role in the default namespace that allows reading ONLY the shared ConfigMap
# by name (resourceNames), preventing access to any other ConfigMap in default.
resource "kubernetes_role" "shared_configmap_reader" {
  metadata {
    name      = "shared-platform-configmap-reader"
    namespace = "default"
  }
  rule {
    api_groups     = [""]
    resources      = ["configmaps"]
    resource_names = [kubernetes_config_map.shared.metadata[0].name]
    verbs          = ["get", "watch", "list"]
  }
}

# Bind only teams that have shared_configmap_access = true.
resource "kubernetes_role_binding" "shared_configmap_reader" {
  for_each = { for k, v in var.teams : k => v if v.shared_configmap_access }
  metadata {
    name      = "shared-configmap-reader-${each.key}"
    namespace = "default"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.shared_configmap_reader.metadata[0].name
  }
  subject {
    kind      = "Group"
    name      = "${each.key}-group"
    api_group = "rbac.authorization.k8s.io"
  }
}

# ─────────────────────────────────────────────────────────────────────────────
# Team ConfigMaps — non-sensitive runtime configuration, scoped to the
# team's own namespace. Pods consume these via envFrom or volume mounts.
# ─────────────────────────────────────────────────────────────────────────────
resource "kubernetes_config_map" "team" {
  for_each = var.teams
  metadata {
    name      = "${each.key}-config"
    namespace = kubernetes_namespace.team[each.key].metadata[0].name
  }
  data = merge(
    {
      PGHOST             = var.rds_host
      PGPORT             = tostring(var.rds_port)
      PGDATABASE         = var.rds_db_name
      AWS_DEFAULT_REGION = var.aws_region
      S3_ENDPOINT_URL    = var.s3_endpoint_url
    },
    each.value.pg_schema != null ? {
      PGSCHEMA = each.value.pg_schema
    } : {},
    each.value.s3_bucket != null ? {
      S3_BUCKET = each.value.s3_bucket
    } : {},
    each.value.mlflow_workspace != null ? {
      MLFLOW_TRACKING_URI = var.mlflow_tracking_uri
      MLFLOW_WORKSPACE    = each.value.mlflow_workspace
    } : {},
    each.value.has_mwaa_access ? {
      MWAA_WEBSERVER_URL = var.mwaa_webserver_url
    } : {},
  )
}

# ─────────────────────────────────────────────────────────────────────────────
# Team Secrets — sensitive credentials, scoped to the team's own namespace.
# Created only for teams that have a pg_username defined.
# ─────────────────────────────────────────────────────────────────────────────
resource "kubernetes_secret" "team_db" {
  for_each = { for k, v in var.teams : k => v if v.pg_username != null }
  metadata {
    name      = "${each.key}-db-credentials"
    namespace = kubernetes_namespace.team[each.key].metadata[0].name
  }
  data = {
    PGUSER     = each.value.pg_username
    PGPASSWORD = each.value.pg_password
  }
  type = "Opaque"
}