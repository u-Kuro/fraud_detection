# Allow teams to see the Postgres version
resource "aws_ssm_parameter" "teams_k8s_namespaces" {
  for_each = var.postgres_teams
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/postgres/version"
  type     = "String"
  value    = aws_db_instance.postgres.engine_version_actual

  depends_on = [
    aws_db_instance.postgres
  ]
}