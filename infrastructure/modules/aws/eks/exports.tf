# Allow teams to see their k8s namespaces in SSM parameter
resource "aws_ssm_parameter" "teams_k8s_namespaces" {
  for_each = var.eks_teams
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/eks/cluster/namespace"
  type     = "String"
  value    = local.eks_teams_namespaces[each.key]

  depends_on = [
    # Waits until teams eks resources are fully functional
    kubectl_manifest.teams
  ]
}
# Allow teams to see access kubeconfig for accessing K8s API
locals { secrets_manager_teams_base64_kubeconfig_path = "eks/base64-kubeconfig" }
resource "aws_secretsmanager_secret" "teams_base64_kubeconfig" {
  for_each                = var.eks_teams
  name                    = "${var.secrets_manager_teams_secret_paths[each.key]}/${local.secrets_manager_teams_base64_kubeconfig_path}"
  recovery_window_in_days = 0

  depends_on = [
    # Waits until teams eks resources are fully functional
    kubectl_manifest.teams
  ]
}
resource "aws_secretsmanager_secret_version" "teams_base64_kubeconfig" {
  for_each  = aws_secretsmanager_secret.teams_base64_kubeconfig
  secret_id = each.value.id

  secret_string_wo         = local.base64_kubeconfig_for_localhost_file_path
  secret_string_wo_version = 1
}
# Allow teams to see that they have base64 kubeconfig for accessing K8s API
resource "aws_ssm_parameter" "teams_base64_kubeconfig" {
  for_each = aws_secretsmanager_secret.teams_base64_kubeconfig
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/${local.secrets_manager_teams_base64_kubeconfig_path}/secretsmanager/secret-id"
  type     = "String"
  value    = each.value.name

  depends_on = [
    aws_secretsmanager_secret_version.teams_base64_kubeconfig
  ]
}