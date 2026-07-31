resource "helm_release" "mlflow" {
  name             = var.mlflow_host
  repository       = "https://community-charts.github.io/helm-charts"
  chart            = "mlflow"
  namespace        = "default"
  create_namespace = true
  timeout          = 300
  wait             = true

  values = [file("${path.root}/helm/mlflow/values.yaml")]

  set = [
    { name = "fullnameOverride",                    value = var.mlflow_host },
    { name = "service.port",                        value = var.mlflow_port },

    { name = "backendStore.postgres.host",          value = var.rds_db_address },
    { name = "backendStore.postgres.port",          value = var.rds_db_port },
    { name = "backendStore.postgres.database",      value = var.rds_db_name },

    { name = "extraEnvVars.MLFLOW_S3_ENDPOINT_URL", value = var.s3_internal_endpoint_url },
    { name = "extraEnvVars.AWS_DEFAULT_REGION",     value = var.s3_mlflow_bucket_aws_region },
    { name = "artifactRoot.s3.bucket",              value = var.s3_mlflow_bucket },
  ]

  set_sensitive = [
    { name = "backendStore.postgres.user",             value = var.mlflow_db_username },
    { name = "backendStore.postgres.password",         value = var.mlflow_db_password },

    { name = "artifactRoot.s3.awsAccessKeyId",         value = var.aws_access_key },
    { name = "artifactRoot.s3.awsSecretAccessKey",     value = var.aws_secret_key },
  ]
}