# Allow admin to see MLflow credential
resource "aws_secretsmanager_secret" "mlflow_credentials" {
  name                    = "admin/rds/postgres/services/mlflow/credential"
  recovery_window_in_days = 0

  depends_on = [postgresql_role.mlflow]
}
resource "aws_secretsmanager_secret_version" "mlflow_credentials" {
  for_each  = aws_secretsmanager_secret.mlflow_credentials
  secret_id = each.value.id

  secret_string_wo = jsonencode({
    username      = postgresql_role.mlflow.name
    password      = postgresql_role.mlflow.password
  })
  secret_string_wo_version = 1

  depends_on = [aws_secretsmanager_secret.mlflow_credentials]
}
# Allow teams to see their Postgres credentials
locals { secrets_manager_teams_postgres_credentials_path = "postgres/credential" }
resource "aws_secretsmanager_secret" "teams_postgres_credentials" {
  for_each                = postgresql_role.teams
  name                    = "${var.secrets_manager_teams_secret_paths[each.key]}/${local.secrets_manager_teams_postgres_credentials_path}"
  recovery_window_in_days = 0

  depends_on = [postgresql_role.teams]
}
resource "aws_secretsmanager_secret_version" "teams_postgres_credentials" {
  for_each  = aws_secretsmanager_secret.teams_postgres_credentials
  secret_id = each.value.id

  secret_string_wo = jsonencode({
    username = local.rds_postgres_teams_usernames[each.key]
    password = local.rds_postgres_teams_passwords[each.key]
  })
  secret_string_wo_version = 1

  depends_on = [aws_secretsmanager_secret.teams_postgres_credentials]
}
# Allow teams to see that they have Postgres credentials
resource "aws_ssm_parameter" "teams_postgres_credentials" {
  for_each = aws_secretsmanager_secret.teams_postgres_credentials
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/${local.secrets_manager_teams_postgres_credentials_path}/secretsmanager/secret-id"
  type     = "String"
  value    = each.value.name

  depends_on = [aws_secretsmanager_secret_version.teams_postgres_credentials]
}
# Allow teams to see their Postgres migration credentials
locals { secrets_manager_teams_postgres_migration_credentials_path = "postgres/migration-credential" }
resource "aws_secretsmanager_secret" "teams_postgres_migration_credentials" {
  for_each                = postgresql_role.teams_migration
  name                    = "${var.secrets_manager_teams_secret_paths[each.key]}/${local.secrets_manager_teams_postgres_migration_credentials_path}"
  recovery_window_in_days = 0

  depends_on = [postgresql_role.teams_migration]
}
resource "aws_secretsmanager_secret_version" "teams_postgres_migration_credentials" {
  for_each  = aws_secretsmanager_secret.teams_postgres_migration_credentials
  secret_id = each.value.id

  secret_string_wo = jsonencode({
    username = local.rds_postgres_teams_migration_usernames[each.key]
    password = local.rds_postgres_teams_migration_passwords[each.key]
  })
  secret_string_wo_version = 1

  depends_on = [aws_secretsmanager_secret.teams_postgres_migration_credentials]
}
# Allow teams to see that they have Postgres migration credentials
resource "aws_ssm_parameter" "teams_postgres_migration_credentials" {
  for_each = aws_secretsmanager_secret.teams_postgres_migration_credentials
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/${local.secrets_manager_teams_postgres_migration_credentials_path}/secretsmanager/secret-id"
  type     = "String"
  value    = each.value.name

  depends_on = [aws_secretsmanager_secret_version.teams_postgres_migration_credentials]
}