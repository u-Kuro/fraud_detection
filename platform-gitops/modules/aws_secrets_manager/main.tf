# SECRETS MANAGER TEAMS' PERMISSIONS
resource "aws_iam_role_policy" "secrets_manager_teams" {
  for_each = local.secrets_manager.users.teams
  role     = local.iam.users.teams[each.key].role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "secretsmanager:*"
        Resource = [
          "${local.secrets_manager_arn}:${each.key}",
          "${local.secrets_manager_arn}:${each.key}-*",
          "${local.secrets_manager_arn}:${each.key}/",
          "${local.secrets_manager_arn}:${each.key}/*",
        ]
      }
    ]
  })
}