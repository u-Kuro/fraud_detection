locals {
  # ECR
  # /arns
  ecr_repository_base_arn = "arn:aws:ecr:*:${var.iam_admin_account_id}:repository"
}