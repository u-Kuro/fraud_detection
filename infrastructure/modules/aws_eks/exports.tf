# Allow teams to see their k8s namespaces in SSM parameter
resource "aws_ssm_parameter" "teams_k8s_namespaces" {
  for_each = var.eks_teams
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/eks/cluster/namespace"
  type     = "String"
  value    = local.eks_teams_namespaces[each.key]

  depends_on = [
    aws_eks_access_entry.teams,
    kubernetes_role_binding.teams
  ]
}
# Allow teams to see access kubeconfig for their CI/CD
locals { secrets_manager_teams_base64_kubeconfig_path = "eks/base64-kubeconfig" }
resource "aws_secretsmanager_secret" "teams_base64_kubeconfig" {
  for_each                = var.eks_teams
  name                    = "${var.secrets_manager_teams_secret_paths[each.key]}/${local.secrets_manager_teams_base64_kubeconfig_path}"
  recovery_window_in_days = 0

  depends_on = [data.external.k3s_configuration]
}
resource "aws_secretsmanager_secret_version" "teams_base64_kubeconfig" {
  for_each  = aws_secretsmanager_secret.teams_base64_kubeconfig
  secret_id = each.value.id

  secret_string_wo         = filebase64(data.external.k3s_configuration.result.kubeconfig_for_localhost_file_path)
  secret_string_wo_version = 1

  depends_on = [
    data.external.k3s_configuration,
    aws_secretsmanager_secret.teams_base64_kubeconfig
  ]
}
# Allow teams to see that they have credentials for their MLflow workspace
resource "aws_ssm_parameter" "teams_base64_kubeconfig" {
  for_each = aws_secretsmanager_secret.teams_base64_kubeconfig
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/${local.secrets_manager_teams_base64_kubeconfig_path}/secretsmanager/secret-id"
  type     = "String"
  value    = each.value.name

  depends_on = [aws_secretsmanager_secret_version.teams_base64_kubeconfig]
}