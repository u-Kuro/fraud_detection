# Allow teams to see info of their MWAA environments
resource "aws_ssm_parameter" "teams_mwaa_environment_names" {
  for_each = aws_mwaa_environment.teams
  name     = "/${var.ssm_teams_parameter_path[each.key]}/MWAA/environment/name"
  type     = "String"
  value    = "s3://${var.s3_teams_mwaa_bucket_name[each.key]}/${each.value.dag_s3_path}"
}
resource "aws_ssm_parameter" "teams_mwaa_environment_dag_s3_uris" {
  for_each = aws_mwaa_environment.teams
  name     = "/${var.ssm_teams_parameter_path[each.key]}/MWAA/environment/dag_s3_uri"
  type     = "String"
  value    = "s3://${var.s3_teams_mwaa_bucket_name[each.key]}/${each.value.dag_s3_path}"
}