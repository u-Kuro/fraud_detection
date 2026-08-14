# Authorize Teams to their ECR repository
locals { ecr_repository_arn = "arn:aws:ecr:*:${var.iam_admin_account_id}:repository" }
resource "aws_iam_role_policy" "ecr_teams" {
  for_each = var.ecr_teams
  role     = var.iam_teams_role_name[each.key]
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
          "${local.ecr_repository_arn}/${each.key}",
          "${local.ecr_repository_arn}/${each.key}/*"
        ]
      }
    ]
  })
}