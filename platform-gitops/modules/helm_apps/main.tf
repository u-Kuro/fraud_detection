locals {
  shared_namespace = "default"

  mlflow_host = "mlflow"
  mlflow_port = 5000
  mlflow_tracking_uri = "http://${local.mlflow_host}:${local.mlflow_port}"
}

resource "helm_release" "mlflow" {
  name             = local.mlflow_host
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
    { name = "artifactRoot.s3.bucket",              value = var.s3_mlflow_bucket },
    { name = "artifactRoot.s3.path",                value = "artifacts" },
    { name = "extraEnvVars.MLFLOW_S3_ENDPOINT_URL", value = var.s3_internal_endpoint_url },
  ]

  set_sensitive = [
    { name = "backendStore.postgres.user",             value = var.mlflow_db_username },
    { name = "backendStore.postgres.password",         value = var.mlflow_db_password },
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

# Non-sensitive infra connectivity — MLE reads this without ever touching platform-gitops.
resource "kubernetes_config_map" "platform_infra" {
  metadata {
    name      = "platform-infra"
    namespace = local.shared_namespace
  }

  data = {
    POSTGRES_HOST           = var.rds_db_address
    POSTGRES_PORT           = var.rds_db_port
    FRAUD_DETECTION_DB_NAME = var.rds_db_name
    MLFLOW_TRACKING_URI     = local.mlflow_tracking_uri
    S3_ENDPOINT_URL         = var.s3_internal_endpoint_url
    AWS_DEFAULT_REGION      = var.s3_mlflow_bucket_aws_region
    S3_MLE_BUCKET           = var.s3_mle_bucket
  }

  depends_on = [helm_release.mlflow]
}