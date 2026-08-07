# TEAM PERMISSIONS
resource "aws_iam_role_policy" "teams" {
  for_each = var.aws.users.teams
  role     = each.value.role.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "secretsmanager:*"
        Resource = [
          "arn:aws:secretsmanager:*:${var.aws.users.admin.account_id}:secret:${each.key}-*",
          "arn:aws:secretsmanager:*:${var.aws.users.admin.account_id}:secret:${each.key}/*"
        ]
      }
    ]
  })
}