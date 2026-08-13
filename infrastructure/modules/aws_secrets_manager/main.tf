# TEAMS' SECRETS MANAGER PERMISSIONS
resource "aws_iam_role_policy" "teams_secrets_manager" {
  for_each = local.secrets_manager.users.teams
  role     = local.iam.users.teams[each.key].role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "secretsmanager:*"
        Resource = [
          "${local.secrets_manager_arn}:${local.secrets_manager_users.teams[each.key].path}",
          "${local.secrets_manager_arn}:${local.secrets_manager_users.teams[each.key].path}-*",
          "${local.secrets_manager_arn}:${local.secrets_manager_users.teams[each.key].path}/",
          "${local.secrets_manager_arn}:${local.secrets_manager_users.teams[each.key].path}/*",
        ]
      }
    ]
  })
}