output "name" {
  value = aws_eks_cluster.main.name
}
output "endpoint" {
  value = aws_eks_cluster.main.endpoint
}

output "oidc_issuer_url" {
  description = "OIDC issuer URL — passed to the aws_iam_oidc module"
  value       = aws_eks_cluster.main.identity[0].oidc[0].issuer
}