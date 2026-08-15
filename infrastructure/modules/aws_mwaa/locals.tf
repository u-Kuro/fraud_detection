locals {
  # MWAA
  # /teams
  mwaa_teams_environment_names        = { for v in var.mwaa_teams : v => v }
  mwaa_teams_environment_dag_s3_paths = { for k in var.mwaa_teams : k => "${var.s3_teams_mwaa_dag_path}/" }

  # Secrets Manager
  # /arns
  secrets_manager_base_arn = "arn:aws:secretsmanager:*:${var.iam_admin_account_id}:secret"
}