# SECRETMANAGER TEAMS' PERMISSIONS
resource "aws_iam_role_policy" "secretmanager_teams" {
  for_each = local.aws.users.secretmanager_teams
  role     = each.value.role.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "secretsmanager:*"
        Resource = [
          "${local.secretsmanager.arn}:${each.key}",
          "${local.secretsmanager.arn}:${each.key}-*",
          "${local.secretsmanager.arn}:${each.key}/",
          "${local.secretsmanager.arn}:${each.key}/*",
        ]
      }
    ]
  })
}