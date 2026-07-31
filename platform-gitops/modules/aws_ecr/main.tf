resource "aws_ecr_repository" "repos" {
  for_each = toset([
    "archive",
    "drift_check",
    "fraud_detection",
    "train_model",
  ])
  name                 = each.key
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}