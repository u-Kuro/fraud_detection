resource "aws_ssm_parameter" "teams_eks_cluster_namespace" {
  for_each = local.eks.users.teams
  name  = "/${local.ssm_parameter.users.teams[each.key].path}/EKS/cluster/namespace"
  type  = "String"
  value = local.eks_users.teams[each.key].kubernetes.namespace
}