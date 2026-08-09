# ECR TEAMS' REPOSITORIES
resource "aws_ecr_repository" "ecr_teams" {
  for_each             = local.ecr_teams_repositories
  name                 = each.value # [team]/[repository]
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}
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
resource "aws_ecr_repository_policy" "ecr_teams" {
  for_each   = aws_ecr_repository.ecr_teams
  repository = each.value.name
  policy = jsonencode({
    Statement = [{
      Effect   = "Allow"
      Action   = "ecr:*"
      Resource = "*"
      Principal = {
        AWS = local.aws.users.ecr_teams[each.key].role.arn
      }
    }]
  })
}