# EKS
# /cluster
output "cluster_name" { value = aws_eks_cluster.main.name }
# /urls
output "cluster_endpoint" { value = aws_eks_cluster.main.endpoint }
output "cluster_ip" { value = regex("https://([^:]+):", aws_eks_cluster.main.endpoint)[0] }
# /teams
output "cluster_teams" { value = var.eks_teams }
output "cluster_teams_namespace" { value = var.eks_teams_namespace }

# Local Files
output "local_files_kubeconfig_container_path" { value = local_sensitive_file.kubeconfig_container.filename }
output "local_files_ecr_registries_path" { value = local_sensitive_file.ecr_registries.filename }