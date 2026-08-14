# TEAMS' MWAA ENVIRONMENT
resource "aws_ssm_parameter" "teams_mwaa_environment_dag_s3_uri" {
  for_each = aws_mwaa_environment.teams
  name     = "/${local.ssm_parameter.users.teams[each.key].path}/MWAA/environment/dag_s3_uri"
  type     = "String"
  value    = "s3://${local.s3.buckets.teams_mwaa[each.key].name}/${each.value.dag_s3_path}"
}