# EKS
# /cluster
output "cluster_name" { value = aws_eks_cluster.main.name }
# /urls
output "cluster_endpoint" { value = aws_eks_cluster.main.endpoint }
# /teams
output "cluster_teams_namespaces" { value = local.eks_teams_namespaces }