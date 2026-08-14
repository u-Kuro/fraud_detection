# TEAMS' CLUSTER
resource "aws_ssm_parameter" "teams_eks_cluster_namespace" {
  for_each = var.eks_teams
  name     = "/${var.ssm_parameter_teams_parameter_path[each.key]}/EKS/cluster/namespace"
  type     = "String"
  value    = var.eks_teams_namespace[each.key]
}