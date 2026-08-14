# Allow teams to manage their own secrets
locals {
  secrets_manager_base_arn = "arn:aws:secretsmanager:*:${var.iam_admin_account_id}:secret"
  secrets_manager_teams_secret_paths = { for v in var.secrets_manager_teams : v => v }
  secrets_manager_teams_secret_arns = {
    for k, v in local.secrets_manager_teams_secret_paths : k => "${local.secrets_manager_base_arn}:${v}"
  }
}
resource "aws_iam_user_policy" "teams" {
  for_each = var.secrets_manager_teams
  user     = var.iam_teams_names[each.key]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "secretsmanager:*"
        Resource = [
          "${local.secrets_manager_teams_secret_arns[each.key]}/",
          "${local.secrets_manager_teams_secret_arns[each.key]}/*",
        ]
      }
    ]
  })
}