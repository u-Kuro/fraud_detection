resource "aws_iam_role" "node" {
  name = "eks_node_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "node_ecr" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

locals {
  team_repositories = toset(flatten([
    for team, values in var.teams : [
      for ecr_repository in values.ecr_repositories :
      "${team}/${ecr_repository}"
    ]
  ]))
}
resource "aws_ecr_repository" "teams" {
  for_each              = local.team_repositories
  name                  = each.value  # [team]/[repository]
  image_tag_mutability  = "MUTABLE"
  force_delete          = true
}
resource "aws_iam_user_policy" "teams" {
  for_each  = var.teams
  name      = "${each.key}_ecr_policy"
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