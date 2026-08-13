output "cluster" {
  value = {
    endpoint = aws_eks_cluster.main.endpoint
    ip       = regex("https://([^:]+):", aws_eks_cluster.main.endpoint)[0]
    name     = aws_eks_cluster.main.name
    users = {
      teams = {
        for k, v in local.eks.users.teams : k => {
          kubernetes = {
            namespace = local.eks_users.teams[k].kubernetes.namespace
          }
        }
      }
    }
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