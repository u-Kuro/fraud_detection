# MWAA
resource "aws_s3_object" "upload_requirements_for_mwaa" {
  for_each = local.s3.buckets.teams_mwaa
  bucket   = each.value.name
  key      = local.s3_mwaa_requirements_path
  source   = local.local_files.mwaa_requirements.file.path
  etag     = filemd5(local.local_files.mwaa_requirements.file.path)
}
resource "aws_s3_object" "upload_kubeconfig_for_mwaa" {
  for_each = local.s3.buckets.teams_mwaa
  bucket   = each.value.name
  key      = "${local.s3_mwaa_dag_path}/${local.s3_kubeconfig_file_path_for_mwaa}"
  source   = local.local_files.kubeconfig.host.file.path
  etag     = filemd5(local.local_files.kubeconfig.host.file.path)
}
resource "aws_mwaa_environment" "teams_mwaa" {
  for_each           = local.mwaa.users.teams
  name               = "${each.key}_MWAA"
  airflow_version    = "2.10.3"
  execution_role_arn = local.iam.users.teams[each.key].role.arn

  source_bucket_arn    = local.s3.buckets.teams_mwaa[each.key].arn
  requirements_s3_path = local.s3_mwaa_requirements_path
  dag_s3_path          = "${local.s3_mwaa_dag_path}/"

  airflow_configuration_options = {
    "secrets.backend" = "airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend"
    "secrets.backend_kwargs" = jsonencode({
      connections_prefix = "${local.airflow_secrets_backend.connections.prefix}/${each.key}"
      variables_prefix   = "${local.airflow_secrets_backend.variables.prefix}/${each.key}"
      sep                = "/"
      endpoint_url       = local.secrets_manager.container.endpoint_url
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
resource "aws_iam_role_policy" "teams_mwaa" {
  for_each = local.mwaa.users.teams
  role     = local.iam.users.teams[each.key].role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "secretsmanager:*"
        Resource = [
          "${local.secrets_manager_airflow.connections.arn}/${each.key}",
          "${local.secrets_manager_airflow.connections.arn}/${each.key}-*",
          "${local.secrets_manager_airflow.connections.arn}/${each.key}/",
          "${local.secrets_manager_airflow.connections.arn}/${each.key}/*",

          "${local.secrets_manager_airflow.variables.arn}/${each.key}",
          "${local.secrets_manager_airflow.variables.arn}/${each.key}-*",
          "${local.secrets_manager_airflow.variables.arn}/${each.key}/",
          "${local.secrets_manager_airflow.variables.arn}/${each.key}/*",
        ]
      },
      {
        Effect = "Deny"
        Action = [
          "s3:DeleteObject",
          "s3:DeleteObjectVersion"
        ]
        Resource = [
          "${local.s3.buckets.teams_mwaa[each.key].arn}/${local.s3_mwaa_requirements_path}",
          "${local.s3.buckets.teams_mwaa[each.key].arn}/${local.s3_mwaa_dag_path}/${local.s3_kubeconfig_file_path_for_mwaa}"
        ]
      }
    ]
  })
}