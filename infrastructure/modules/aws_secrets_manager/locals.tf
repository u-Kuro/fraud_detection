locals {
  # Secrets Manager
  # /arns
  secrets_manager_base_arn = "arn:aws:secretsmanager:*:${var.iam_admin_account_id}:secret"
  # /teams
  secrets_manager_teams_secret_paths = { for v in var.secrets_manager_teams : v => v }
  secrets_manager_teams_secret_arns = {
    for k, v in local.secrets_manager_teams_secret_paths : k => "${local.secrets_manager_base_arn}:${v}"
  }
}