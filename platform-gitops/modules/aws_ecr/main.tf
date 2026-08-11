# ECR TEAMS' PERMISSIONS
resource "aws_iam_role_policy" "ecr_teams" {
  for_each = local.aws.users.ecr_teams
  role     = each.value.role.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = "ecr:*"
        Resource = [
          "arn:aws:ecr:*:${local.aws.users.admin.account_id}:repository/${each.key}",
          "arn:aws:ecr:*:${local.aws.users.admin.account_id}:repository/${each.key}/*"
        ]
      },
    ]
  })
}