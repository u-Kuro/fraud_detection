# Allow teams to see the Postgres version
resource "aws_ssm_parameter" "teams_postgres_version" {
  for_each = var.postgres_teams
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/postgres/version"
  type     = "String"
  value    = aws_db_instance.postgres.engine_version_actual

  depends_on = [
    # Waits until postgres is fully functional
    aws_iam_role_policy.rds,
    data.external.postgres_configuration,
  ]
}