# MWAA
resource "aws_s3_object" "upload_requirements_for_mwaa" {
  for_each = local.s3.buckets.mwaa_teams
  bucket   = each.value.arn
  key      = local.s3_mwaa_requirements_path
  source   = local.local_files.mwaa_requirements.file.path
  etag     = filemd5(local.local_files.mwaa_requirements.file.path)
}
resource "aws_s3_object" "upload_kubeconfig_for_mwaa" {
  for_each = local.s3.buckets.mwaa_teams
  bucket   = each.value.arn
  key      = "${local.s3_mwaa_dag_path}/${local.s3_kubeconfig_file_path_for_mwaa}"
  source   = local.local_files.kubeconfig.host.file.path
  etag     = filemd5(local.local_files.kubeconfig.host.file.path)
}
resource "aws_mwaa_environment" "mwaa" {
  for_each           = local.aws.users.mwaa_teams
  name               = "mwaa_${each.key}"
  airflow_version    = "2.10.3"
  execution_role_arn = each.value.role.arn

  source_bucket_arn  = local.s3.buckets.mwaa_teams[each.key].arn
  requirements_s3_path  = local.s3_mwaa_requirements_path
  dag_s3_path        = "${local.s3_mwaa_dag_path}/"

  airflow_configuration_options = {
    "secrets.backend" = "airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend"
    "secrets.backend_kwargs" = jsonencode({
      connections_prefix = "${local.airflow_secrets_backend.connections.prefix}/${each.key}"
      variables_prefix   = "${local.airflow_secrets_backend.variables.prefix}/${each.key}"
      sep                = "/"
      endpoint_url       = local.secretsmanager.container.endpoint_url
    })
  }

  network_configuration {
    security_group_ids = ["sg-00000000000000001"]
    subnet_ids         = ["subnet-00000000000000001", "subnet-00000000000000002"]
  }

  depends_on = [
    aws_s3_object.upload_requirements_for_mwaa,
    aws_s3_object.upload_kubeconfig_for_mwaa,
  ]
}
# MWAA TEAMS' PERMISSIONS
resource "aws_iam_role_policy" "mwaa_teams" {
  for_each = local.aws.users.mwaa_teams
  role     = each.value.role.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "secretsmanager:*"
        Resource = [
          "${local.secretsmanager_airflow.connections.arn}/${each.key}",
          "${local.secretsmanager_airflow.connections.arn}/${each.key}-*",
          "${local.secretsmanager_airflow.connections.arn}/${each.key}/",
          "${local.secretsmanager_airflow.connections.arn}/${each.key}/*",

          "${local.secretsmanager_airflow.variables.arn}/${each.key}",
          "${local.secretsmanager_airflow.variables.arn}/${each.key}-*",
          "${local.secretsmanager_airflow.variables.arn}/${each.key}/",
          "${local.secretsmanager_airflow.variables.arn}/${each.key}/*",
        ]
      },
    ]
  })
}