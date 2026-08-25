# Allow teams to see info of their MLflow workspace
resource "aws_ssm_parameter" "teams_mlflow_workspace" {
  for_each = kubernetes_job.teams
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/eks/cluster/mlflow/workspace"
  type     = "String"
  value    = local.mlflow_teams_workspace_names[each.key]

  depends_on = [
    # Waits until teams MLflow resources are fully functional
    kubernetes_manifest.ingress_route,
  ]
}
# Allow teams to see their credentials for their MLflow workspace
locals { secrets_manager_teams_mlflow_credentials_path = "eks/cluster/mlflow/credential" }
resource "aws_secretsmanager_secret" "teams_mlflow_credentials" {
  for_each                = kubernetes_job.teams
  name                    = "${var.secrets_manager_teams_secret_paths[each.key]}/${local.secrets_manager_teams_mlflow_credentials_path}"
  recovery_window_in_days = 0

  depends_on = [
    # Waits until teams MLflow resources are fully functional
    kubernetes_manifest.ingress_route,
  ]
}
resource "aws_secretsmanager_secret_version" "teams_mlflow_credentials" {
  for_each  = aws_secretsmanager_secret.teams_mlflow_credentials
  secret_id = each.value.id

  secret_string_wo = jsonencode({
    username = local.mlflow_teams_usernames[each.key]
    password = local.mlflow_teams_passwords[each.key]
  })
  secret_string_wo_version = 1
}
# Allow teams to see that they have credentials for their MLflow workspace
resource "aws_ssm_parameter" "teams_mlflow_credentials" {
  for_each = aws_secretsmanager_secret.teams_mlflow_credentials
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/${local.secrets_manager_teams_mlflow_credentials_path}/secretsmanager/secret-id"
  type     = "String"
  value    = each.value.name

  depends_on = [
    aws_secretsmanager_secret_version.teams_mlflow_credentials[each.key]
  ]
}
