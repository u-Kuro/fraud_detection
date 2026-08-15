# Allow teams to see their k8s namespaces in SSM parameter
resource "aws_ssm_parameter" "teams_k8s_namespaces" {
  for_each = var.eks_teams
  name     = "/${var.ssm_teams_parameter_path[each.key]}/eks/cluster/namespace"
  type     = "String"
  value    = local.eks_teams_namespaces[each.key]

  depends_on = [
    aws_eks_access_entry.teams,
    kubernetes_role_binding.teams
  ]
}