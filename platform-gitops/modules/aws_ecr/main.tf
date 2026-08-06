# REPOSITORIES
locals {
  team_repositories = toset(flatten([
    for team, values in var.teams : [
      for repository in values.ecr.repositories :
      "${team}/${repository}"
    ]
  ]))
}
resource "aws_ecr_repository" "teams" {
  for_each             = local.team_repositories
  name                 = each.value # [team]/[repository]
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}
# TEAM PERMISSIONS
resource "aws_iam_role_policy" "teams" {
  for_each = var.teams
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
          "arn:aws:ecr:*:${var.aws_admin.account_id}:repository/${each.key}",
          "arn:aws:ecr:*:${var.aws_admin.account_id}:repository/${each.key}/*"
        ]
      },
    ]
  })
}
resource "aws_ecr_repository_policy" "ecr" {
  for_each   = aws_ecr_repository.teams
  repository = each.value.name
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = "ecr:*"
      Resource = "*"
      Principal = {
        AWS = var.teams[each.key].role_arn
      }
    }]
  })
}