# TEAMS' MLFLOW WORKSPACE
resource "aws_ssm_parameter" "teams_mlflow_workspace" {
  for_each = kubernetes_job.mlflow_teams
  name     = "/${local.ssm_parameter.users.teams[each.key].path}/EKS/cluster/Mlflow/workspace"
  type     = "String"
  value    = each.value.spec[0].template[0].spec[0]
}
# TEAMS' MLFLOW CREDENTIAL
resource "aws_secretsmanager_secret" "teams_iam_credential" {
  for_each                = local.iam.users.teams
  name                    = "${local.secrets_manager.users.teams[each.key].path}/EKS/cluster/Mlflow/credential"
  recovery_window_in_days = 0
}
resource "aws_secretsmanager_secret_version" "teams_iam_credential" {
  for_each  = aws_secretsmanager_secret.teams_iam_credential
  secret_id = each.value.id

  secret_string_wo = jsonencode({
    access_key_id     = aws_iam_access_key.teams[each.key].id
    secret_access_key = aws_iam_access_key.teams[each.key].secret
  })
  secret_string_wo_version = 1

  depends_on = [
    aws_iam_access_key.teams,
    aws_secretsmanager_secret.teams_iam_credential
  ]
}
# > TEAMS' REFERENCE
resource "aws_ssm_parameter" "teams_mwaa_environment_dag_s3_uri" {
  for_each = aws_mwaa_environment.teams
  name     = "/${local.ssm_parameter.users.teams[each.key].path}${trimprefix(aws_secretsmanager_secret.teams_iam_credential[each.key].name, local.secrets_manager.users.teams[each.key].path)}/secretsmanager/secret-id"
  type     = "String"
  value    = aws_secretsmanager_secret.teams_iam_credential[each.key].name

  depends_on = [aws_secretsmanager_secret.teams_iam_credential]
}
