locals {
  shared_namespace = "default"
}
# MLflow
resource "helm_release" "mlflow" {
  name             = "mlflow"
  repository       = "https://community-charts.github.io/helm-charts"
  chart            = "mlflow"
  namespace        = local.shared_namespace
  create_namespace = true
  timeout          = 300
  wait             = true

  values = [file("${path.root}/helm/mlflow/values.yaml")]

  # Dynamic values injected at apply time.
  set {
    name  = "backendStore.databaseMigration"
    value = true
  }
  set {
    name  = "backendStore.postgres.enabled"
    value = true
  }
  set {
    name  = "backendStore.postgres.host"
    value = var.rds_db_address
  }
  set {
    name  = "backendStore.postgres.port"
    value = var.rds_db_port
  }
  set {
    name  = "backendStore.postgres.database"
    value = var.rds_db_name
  }
  set {
    name  = "backendStore.postgres.user"
    value = var.rds_db_username
  }
  set_sensitive {
    name  = "backendStore.postgres.password"
    value = var.rds_db_password
  }

  set {
    name  = "artifactRoot.s3.enabled"
    value = true
  }
  set {
    name  = "extraEnvVars.MLFLOW_S3_ENDPOINT_URL"
    value = var.s3_internal_endpoint_url
  }
  set {
    name  = "artifactRoot.s3.bucket"
    value = var.s3_mlflow_bucket_name
  }
  set {
    name  = "artifactRoot.s3.awsAccessKeyId"
    value = var.aws_access_key
  }
  set {
    name  = "artifactRoot.s3.awsSecretAccessKey"
    value = var.aws_secret_key
  }
  # TODO - set stuff from /helm/mlflow/values.yaml to here
  # TODO - check if extraEnvVars keys there can be in their own category. find if their categ has them
  # TODO - check if service type and port is needed

}

# Kubernetes Secret for FastAPI
# Stored as a proper k8s Secret so sensitive values are not in the Helm values.
resource "kubernetes_secret" "fraud_detection" {
  metadata {
    name      = "fraud_detection_secrets"
    namespace = "default"
  }

  data = {
    POSTGRES_HOST          = var.rds_db_address
    POSTGRES_DB            = var.rds_db_name
    POSTGRES_USER          = var.rds_db_username
    POSTGRES_PASSWORD      = var.rds_db_password
    MLFLOW_S3_ENDPOINT_URL = var.s3_internal_endpoint_url
    AWS_ACCESS_KEY_ID      = var.aws_access_key
    AWS_SECRET_ACCESS_KEY  = var.aws_secret_key
    AWS_DEFAULT_REGION     = var.aws_region
    MLFLOW_TRACKING_URI    = "http://mlflow:5000"
    SLACK_BOT_TOKEN        = var.slack_bot_token
    SLACK_APP_TOKEN        = var.slack_app_token
  }

  depends_on = [helm_release.mlflow]
}

# FastAPI (local Helm chart)
resource "helm_release" "fraud_detection" {
  name      = "fraud_detection"
  chart     = "${path.root}/helm/fraud_detection"
  namespace = local.shared_namespace
  create_namespace = true
  timeout   = 300
  wait      = true

  values = [file("${path.root}/helm/fraud_detection/values.yaml")]

  depends_on = [kubernetes_secret.fraud_detection]
}
