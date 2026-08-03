output "name" {
  value = aws_eks_cluster.eks.name
}
output "endpoint" {
  value = aws_eks_cluster.eks.endpoint
}

output "ecr_secret_name" {
  value = var.ecr_registry_secret_name
}