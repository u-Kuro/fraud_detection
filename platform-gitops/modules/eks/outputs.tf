output "cluster_name" {
  value = aws_eks_cluster.eks.name
}

output "setup_complete" {
  value = terraform_data.init.id
}

output "kubeconfig_file_path" {
  description = "Host-patched kubeconfig for kubectl from Windows host"
  value       = "${path.root}/kubeconfig/k3s.yaml"
}