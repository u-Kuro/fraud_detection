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

# Non-sensitive infrastructure connectivity facts.
# MLE pods mount this via envFrom.configMapRef alongside their own secret.
# Platform team owns all values here — none are MLE business logic.
resource "kubernetes_config_map" "platform_infrastructure" {
  metadata {
    name      = "platform-infrastructure"
    namespace = local.shared_namespace
  }

  data = {
    PGHOST              = var.rds_db_address
    PGPORT              = var.rds_db_port
    PGDATABASE          = var.rds_db_name

    AWS_DEFAULT_REGION  = var.aws_region
    AWS_ENDPOINT_URL_S3 = var.s3_internal_endpoint_url

    MLFLOW_TRACKING_URI = local.mlflow_tracking_uri

    S3_MLE_BUCKET       = var.s3_mle_bucket
    S3_ENDPOINT_URL     = var.s3_internal_endpoint_url

    MWAA_WEBSERVER_URL = var.mwaa_webserver_url
  }

  depends_on = [helm_release.mlflow]
}