resource "aws_ecr_repository" "repos" {
  for_each             = toset(var.repositories)
  name                 = each.key
  image_tag_mutability = "MUTABLE"
  force_delete         = true
}