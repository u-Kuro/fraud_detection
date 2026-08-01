locals {
  # Flatten teams × repos into a map keyed by "<team>/<repo>"
  team_repos = merge([
    for team_key, team in var.teams : {
      for repo in team.ecr_repos :
      "${team_key}/${repo}" => {
        team     = team_key
        repo     = repo
        role_arn = var.team_role_arns[team_key]
      }
    }
  ]...)
}

resource "aws_ecr_repository" "team_repos" {
  for_each             = local.team_repos
  name                 = each.key            # e.g. "mle/fraud_detection"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

resource "aws_ecr_repository_policy" "team_repos" {
  for_each   = local.team_repos
  repository = aws_ecr_repository.team_repos[each.key].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowTeamPushOnly"
        Effect = "Allow"
        Principal = { AWS = each.value.role_arn }
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
        ]
      }
    ]
  })
}