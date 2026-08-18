# Set Python package requirements for MWAA environments
resource "aws_s3_object" "upload_requirements_for_mwaa" {
  for_each = var.mwaa_teams
  bucket   = var.s3_teams_mwaa_bucket_name[each.key]
  key      = var.s3_teams_mwaa_requirements_file_path
  source   = var.local_files_mwaa_requirements_file_path
  etag     = filemd5(var.local_files_mwaa_requirements_file_path)
}
# Upload K8s cluster credential file in MWAA environments for authentication
resource "aws_s3_object" "upload_kubeconfig_for_mwaa" {
  for_each = var.mwaa_teams
  bucket   = var.s3_teams_mwaa_bucket_name[each.key]
  key      = "${var.s3_teams_mwaa_dag_path}/${var.s3_teams_mwaa_kubeconfig_file_path}"
  source   = var.local_files_kubeconfig_container_file_path
  etag     = filemd5(var.local_files_kubeconfig_container_file_path)
}
# Create MWAA environments for each team
locals {
  mwaa_teams_airflow_secrets_backend_connections_prefixes = { for v in var.mwaa_teams : k => "airflow/connections/${v}" }
  mwaa_teams_airflow_secrets_backend_variables_prefixes   = { for v in var.mwaa_teams : k => "airflow/variables/${v}" }
}
resource "aws_mwaa_environment" "teams" {
  for_each           = var.mwaa_teams
  name               = local.mwaa_teams_environment_names[each.key]
  airflow_version    = "2.10.4"
  execution_role_arn = var.iam_teams_role_arns[each.key]

  source_bucket_arn    = var.s3_teams_mwaa_bucket_arn[each.key]
  requirements_s3_path = var.s3_teams_mwaa_requirements_file_path
  dag_s3_path          = local.mwaa_teams_environment_dag_s3_paths[each.key]

  airflow_configuration_options = {
    "secrets.backend" = "airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend"
    "secrets.backend_kwargs" = jsonencode({
      connections_prefix = local.mwaa_teams_airflow_secrets_backend_connections_prefixes[each.key]
      variables_prefix   = local.mwaa_teams_airflow_secrets_backend_variables_prefixes[each.key]
      sep                = "/"
      endpoint_url       = var.secrets_manager_url
    })
  }

  network_configuration {
    security_group_ids = ["sg-00000000000000000", "sg-00000000000000001"]
    subnet_ids         = ["subnet-00000000000000000", "subnet-00000000000000001"]
  }

  depends_on = [
    aws_s3_object.upload_requirements_for_mwaa,
    aws_s3_object.upload_kubeconfig_for_mwaa,
  ]
}
# Allow teams to manage attached repositories in their MWAA environments
locals {
  secrets_manager_mwaa_teams_airflow_secrets_backend_connections_arns = {
    for k, v in local.mwaa_teams_airflow_secrets_backend_connections_prefixes : k => "${local.secrets_manager_base_arn}:${v}"
  }
  secrets_manager_mwaa_teams_airflow_secrets_backend_variables_arns = {
    for k, v in local.mwaa_teams_airflow_secrets_backend_variables_prefixes : k => "${local.secrets_manager_base_arn}:${v}"
  }
}
resource "aws_iam_user_policy" "teams" {
  for_each = var.mwaa_teams
  user     = var.iam_teams_names[each.key]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "secretsmanager:*"
        Resource = [
          # connections
          "${local.secrets_manager_mwaa_teams_airflow_secrets_backend_connections_arns[each.key]}/",
          "${local.secrets_manager_mwaa_teams_airflow_secrets_backend_connections_arns[each.key]}/*",
          # variables
          "${local.secrets_manager_mwaa_teams_airflow_secrets_backend_variables_arns[each.key]}/",
          "${local.secrets_manager_mwaa_teams_airflow_secrets_backend_variables_arns[each.key]}/*",
        ]
      },
      {
        Effect = "Deny"
        Action = [
          "s3:DeleteObject",
          "s3:DeleteObjectVersion"
        ]
        Resource = [
          aws_s3_object.upload_requirements_for_mwaa[each.key].arn,
          aws_s3_object.upload_kubeconfig_for_mwaa[each.key].arn
        ]
      }
    ]
  })
}