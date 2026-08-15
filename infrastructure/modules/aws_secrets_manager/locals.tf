locals {
  # Secrets Manager
  # /arns
  secrets_manager_base_arn = "arn:aws:secretsmanager:*:${var.iam_admin_account_id}:secret"
  # /teams
  secrets_manager_teams_secret_paths = { for v in var.secrets_manager_teams : v => v }
}