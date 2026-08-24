# Allow teams to see info of their MWAA environments
resource "aws_ssm_parameter" "teams_mwaa_environment_names" {
  for_each = aws_mwaa_environment.teams
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/mwaa/environment/name"
  type     = "String"
  value    = local.mwaa_teams_environment_names[each.key]

  depends_on = [aws_mwaa_environment.teams]
}
# > Not working with current setup
resource "aws_ssm_parameter" "teams_mwaa_environment_dag_s3_uris" {
  for_each = aws_mwaa_environment.teams
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/mwaa/environment/dag-s3-uri"
  type     = "String"
  value    = "s3://${var.s3_teams_mwaa_bucket_names[each.key]}/${local.mwaa_teams_environment_dag_s3_paths[each.key]}"

  depends_on = [aws_mwaa_environment.teams]
}
# Replacements for the current setup
resource "aws_ssm_parameter" "teams_airflow_container_name" {
  for_each = aws_mwaa_environment.teams
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/mwaa/environment/container-name"
  type     = "String"
  value    = data.external.airflow_configuration.result.airflow_container_name

  depends_on = [aws_mwaa_environment.teams]
}
resource "aws_ssm_parameter" "teams_airflow_container_dag_directory_path" {
  for_each = aws_mwaa_environment.teams
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/mwaa/environment/dag-directory-path"
  type     = "String"
  value    = data.external.airflow_configuration.result.airflow_container_dag_directory_path

  depends_on = [aws_mwaa_environment.teams]
}