output "name" {
  value = aws_eks_cluster.eks.name
}
output "endpoint" {
  value = aws_eks_cluster.eks.endpoint
}
output "ip" {
  value = regex("https://([^:]+):", aws_eks_cluster.eks.endpoint)[0]
}

output "kubeconfig_container_file_path" {
  value = local_sensitive_file.kubeconfig_container.filename
}