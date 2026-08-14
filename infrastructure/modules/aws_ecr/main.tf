# Allow teams to manage their ECR repository
locals { ecr_repository_base_arn = "arn:aws:ecr:*:${var.iam_admin_account_id}:repository" }
resource "aws_iam_user_policy" "teams" {
  for_each = var.ecr_teams
  user     = var.iam_teams_names[each.key]
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
          "${local.ecr_repository_base_arn}/${each.key}",
          "${local.ecr_repository_base_arn}/${each.key}/*"
        ]
      }
    ]
  })
}