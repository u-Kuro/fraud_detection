# EKS
# /cluster
output "cluster_name" { value = aws_eks_cluster.main.name }
# /urls
output "container_ip" { value = data.external.k3s_configuration.result.k3s_container_ip }
output "container_host_port" { value = data.external.k3s_configuration.result.k3s_container_host_port }
output "host_url" { value = aws_eks_cluster.main.endpoint }
# /teams
output "cluster_teams_namespaces" { value = local.eks_teams_namespaces }