output "cluster" {
  value = {
    endpoint = aws_eks_cluster.eks.endpoint
    ip       = regex("https://([^:]+):", aws_eks_cluster.eks.endpoint)[0]
    name     = aws_eks_cluster.eks.name
  }
}

output "local_files" {
  value = {
    kubeconfig_container = {
      path = local_sensitive_file.kubeconfig_container.filename
    }
    ecr_registries = {
      path = local_sensitive_file.ecr_registries.filename
    }
  }
}