# ECR TEAMS' PERMISSIONS
resource "aws_iam_role_policy" "ecr_teams" {
  for_each = local.ecr.users.teams
  role     = local.iam.users.teams[each.key].role.name
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
          "arn:aws:ecr:*:${local.iam.users.admin.account_id}:repository/${each.key}",
          "arn:aws:ecr:*:${local.iam.users.admin.account_id}:repository/${each.key}/*"
        ]
      },
    ]
  })
}