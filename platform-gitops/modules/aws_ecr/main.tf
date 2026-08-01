locals {
  # Declare which repos belong to each team.
  # To add a new repo for mle: add its name to the list.
  # To add a new team: add an entry key with its repo list.
  team_repositories = {
    mle = [
      "archive",
      "drift_check",
      "fraud_detection",
      "train_model",
    ]
  }

  # TODO - update ecr calls to e.g. mle/fraud_detection
  # Flatten into a map keyed by "<team>/<repo>" for for_each.
  repository_entries = merge([
    for team, repos in local.team_repositories : {
      for repo in repos : "${team}/${repo}" => {
        full_name = "${team}/${repo}"
        team      = team
      }
    }
  ]...)
}

resource "aws_ecr_repository" "repos" {
  for_each = local.repository_entries

  name                 = each.value.full_name   # e.g. "mle/fraud_detection"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}

# ── Repository Policy — only the owning team's role may push ─────────────────
# MiniStack: simulated — policy is stored but not enforced at the API level.
resource "aws_ecr_repository_policy" "team_push" {
  for_each   = local.repository_entries
  repository = aws_ecr_repository.repos[each.key].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowTeamPushPull"
        Effect = "Allow"
        Principal = {
          AWS = var.team_role_arns[each.value.team]
        }
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchGetImage",
          "ecr:CompleteLayerUpload",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories",
          "ecr:GetDownloadUrlForLayer",
          "ecr:InitiateLayerUpload",
          "ecr:ListImages",
          "ecr:PutImage",
          "ecr:UploadLayerPart",
        ]
      }
    ]
  })
}

# ── IAM Role Policy — scoped to each team's own prefix ───────────────────────
# Each unique team gets exactly one policy covering all its repos.
# MiniStack: simulated.
resource "aws_iam_role_policy" "team_ecr_access" {
  for_each = toset(keys(local.team_repositories))

  name = "${each.key}_ecr_push_pull"
  role = var.team_role_names[each.key]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "TeamECRPushPull"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:BatchGetImage",
          "ecr:CompleteLayerUpload",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories",
          "ecr:GetDownloadUrlForLayer",
          "ecr:InitiateLayerUpload",
          "ecr:ListImages",
          "ecr:PutImage",
          "ecr:UploadLayerPart",
        ]
        # Wildcard scoped to the team's own prefix only
        Resource = "arn:aws:ecr:*:${var.aws_account_id}:repository/${each.key}/*"
      }
    ]
  })
}