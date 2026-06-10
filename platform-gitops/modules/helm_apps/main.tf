locals {
  shared_namespace = "default"

  mlflow_host = "mlflow"
  mlflow_port = 5000

  fraud_detection_host = "fraud_detection"
  fraud_detection_port = 30000
  fraud_detection_secret = "fraud-detection-secret"
}

resource "helm_release" "mlflow" {
  name              = local.mlflow_host
  repository       = "https://community-charts.github.io/helm-charts"
  chart            = "mlflow"
  namespace        = local.shared_namespace
  create_namespace = true
  timeout          = 300
  wait             = true

  values = [file("${path.root}/helm/mlflow/values.yaml")]

  set = [
    { name = "fullnameOverride",                    value = local.mlflow_host },
    { name = "service.port",                        value = local.mlflow_port },
    { name = "backendStore.postgres.host",          value = var.rds_db_address },
    { name = "backendStore.postgres.port",          value = var.rds_db_port },
    { name = "backendStore.postgres.database",      value = var.rds_db_name },
    { name = "extraEnvVars.AWS_DEFAULT_REGION",     value = var.s3_mlflow_bucket_aws_region },
    { name = "artifactRoot.s3.bucket",              value = var.s3_mlflow_bucket_name },
    { name = "extraEnvVars.MLFLOW_S3_ENDPOINT_URL", value = var.s3_internal_endpoint_url },
  ]

  set_sensitive = [
    { name = "backendStore.postgres.user",             value = var.rds_db_username },
    { name = "backendStore.postgres.password",         value = var.rds_db_password },
    { name = "artifactRoot.s3.awsAccessKeyId",         value = var.aws_access_key },
    { name = "artifactRoot.s3.awsSecretAccessKey",     value = var.aws_secret_key },
  ]
  # TODO - set stuff from /helm/mlflow/values.yaml to here
  # TODO - check if extraEnvVars keys there can be in their own category. find if their categ has them
  # TODO - check if service type and port is needed in two yaml? what is it for?
  # TODO - is ```localhost:4566/000000000000.dkr.ecr.us-east-1.amazonaws.com/my-app``` just randomly set here initially? which part is random here.
  # TODO - explain all parts of _helpers.tpl. and whats tpl?
  # TODO - explain all {{ }} types that are used in all files since im new to it.
  # TODO - explain all keys and values in all yaml
}

# Kubernetes Secret for FastAPI
# Stored as a proper k8s Secret so sensitive values are not in the Helm values.
resource "kubernetes_secret" "fraud_detection" {
  metadata {
    name      = local.fraud_detection_secret
    namespace = "default"
  }

  data = {
    POSTGRES_HOST          = var.rds_db_address
    POSTGRES_PORT          = var.rds_db_port
    POSTGRES_DB            = var.rds_db_name
    POSTGRES_USER          = var.rds_db_username
    POSTGRES_PASSWORD      = var.rds_db_password
    MLFLOW_S3_ENDPOINT_URL = var.s3_internal_endpoint_url
    MLFLOW_TRACKING_URI    = "http://${local.mlflow_host}:${local.mlflow_port}"
    SLACK_BOT_TOKEN        = var.slack_bot_token
    SLACK_APP_TOKEN        = var.slack_app_token
  }

  depends_on = [helm_release.mlflow]
}

resource "helm_release" "fraud_detection" {
  name              = local.fraud_detection_host
  chart             = "${path.root}/helm/fraud_detection"
  namespace         = local.shared_namespace
  create_namespace  = true
  timeout           = 300
  wait              = true

  values = [file("${path.root}/helm/fraud_detection/values.yaml")]

  set = [
    { name = "service.port",              value = local.fraud_detection_port },
    { name = "service.nodePort",          value = local.fraud_detection_port },
    { name = "image.repository",          value = "${var.ecr_registry_endpoint}/${var.aws_account_id}.dkr.ecr.${var.ecr_region}.amazonaws.com/${var.ecr_repository_name}" },
    { name = "imagePullSecrets[0].name",  value = var.ecr_registry_secret_name },
    { name = "secretName",                value = local.fraud_detection_secret },
  ]

  depends_on = [kubernetes_secret.fraud_detection]
}
