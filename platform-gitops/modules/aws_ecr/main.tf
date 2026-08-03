locals {
  team_repositories = toset(flatten([
    for team, values in var.teams : [
      for ecr_repository in values.ecr_repositories : "${team}/${ecr_repository}"
    ]
  ]))
}

resource "aws_ecr_repository" "team_repositories" {
  for_each              = keys(local.team_repositories)
  name                  = each.value  # [team]/[repository]
  image_tag_mutability  = "MUTABLE"
  force_delete          = true
}

resource "aws_iam_user_policy" "team_ecr_policies" {
  for_each  = var.teams
  name      = "${each.value.name}_ecr_policy"
  user      = each.value.name

  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
        Resource = "arn:aws:ecr:*:${var.aws_account_id}:repository/${each.key}/*"
      }
    ]
  })
}