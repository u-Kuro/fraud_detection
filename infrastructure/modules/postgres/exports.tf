# Allow admin to see MLflow credential
resource "aws_secretsmanager_secret" "mlflow_credentials" {
  name                    = "admin/rds/postgres/services/mlflow/credential"
  recovery_window_in_days = 0

  depends_on = [
    postgresql_grant.mlflow_database,
    postgresql_grant.mlflow_schema,
    postgresql_grant.mlflow_table,
    postgresql_grant.mlflow_sequence,
  ]
}
resource "aws_secretsmanager_secret_version" "mlflow_credentials" {
  secret_id = aws_secretsmanager_secret.mlflow_credentials.id

  secret_string_wo = jsonencode({
    username = postgresql_role.mlflow.name
    password = postgresql_role.mlflow.password
  })
  secret_string_wo_version = 1
}
# Allow teams to see their Postgres credentials
locals { secrets_manager_teams_postgres_credentials_path = "postgres/credential" }
resource "aws_secretsmanager_secret" "teams_postgres_credentials" {
  for_each                = postgresql_role.teams
  name                    = "${var.secrets_manager_teams_secret_paths[each.key]}/${local.secrets_manager_teams_postgres_credentials_path}"
  recovery_window_in_days = 0

  depends_on = [
    postgresql_grant.teams_database[each.key],
    postgresql_grant.teams_schema[each.key],
    postgresql_grant.teams_table[each.key],
    postgresql_grant.teams_sequence[each.key],
    postgresql_grant.teams_migration_database[each.key],
    postgresql_grant.teams_migration_schema[each.key],
    postgresql_grant.teams_migration_table[each.key],
    postgresql_grant.teams_migration_sequence[each.key],
    postgresql_default_privileges.teams_future_tables[each.key],
    postgresql_default_privileges.teams_future_sequences[each.key],
  ]
}
resource "aws_secretsmanager_secret_version" "teams_postgres_credentials" {
  for_each  = aws_secretsmanager_secret.teams_postgres_credentials
  secret_id = each.value.id

  secret_string_wo = jsonencode({
    username = local.rds_postgres_teams_usernames[each.key]
    password = local.rds_postgres_teams_passwords[each.key]
  })
  secret_string_wo_version = 1
}
# Allow teams to see that they have Postgres credentials
resource "aws_ssm_parameter" "teams_postgres_credentials" {
  for_each = aws_secretsmanager_secret.teams_postgres_credentials
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/${local.secrets_manager_teams_postgres_credentials_path}/secretsmanager/secret-id"
  type     = "String"
  value    = each.value.name

  depends_on = [
    aws_secretsmanager_secret_version.teams_postgres_credentials[each.key]
  ]
}
# Allow teams to see their Postgres migration credentials
locals { secrets_manager_teams_postgres_migration_credentials_path = "postgres/migration-credential" }
resource "aws_secretsmanager_secret" "teams_postgres_migration_credentials" {
  for_each                = postgresql_role.teams_migration
  name                    = "${var.secrets_manager_teams_secret_paths[each.key]}/${local.secrets_manager_teams_postgres_migration_credentials_path}"
  recovery_window_in_days = 0

  depends_on = [
    postgresql_grant.teams_database[each.key],
    postgresql_grant.teams_schema[each.key],
    postgresql_grant.teams_table[each.key],
    postgresql_grant.teams_sequence[each.key],
    postgresql_grant.teams_migration_database[each.key],
    postgresql_grant.teams_migration_schema[each.key],
    postgresql_grant.teams_migration_table[each.key],
    postgresql_grant.teams_migration_sequence[each.key],
    postgresql_default_privileges.teams_future_tables[each.key],
    postgresql_default_privileges.teams_future_sequences[each.key],
  ]
}
resource "aws_secretsmanager_secret_version" "teams_postgres_migration_credentials" {
  for_each  = aws_secretsmanager_secret.teams_postgres_migration_credentials
  secret_id = each.value.id

  secret_string_wo = jsonencode({
    username = local.rds_postgres_teams_migration_usernames[each.key]
    password = local.rds_postgres_teams_migration_passwords[each.key]
  })
  secret_string_wo_version = 1
}
# Allow teams to see that they have Postgres migration credentials
resource "aws_ssm_parameter" "teams_postgres_migration_credentials" {
  for_each = aws_secretsmanager_secret.teams_postgres_migration_credentials
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/${local.secrets_manager_teams_postgres_migration_credentials_path}/secretsmanager/secret-id"
  type     = "String"
  value    = each.value.name

  depends_on = [
    aws_secretsmanager_secret_version.teams_postgres_migration_credentials[each.key]
  ]
}
# Allow teams to see their Postgres URI with credentials
locals { secrets_manager_teams_postgres_migration_database_url_path = "postgres/migration-database-url" }
resource "aws_secretsmanager_secret" "teams_postgres_migration_database_url" {
  for_each                = postgresql_role.teams
  name                    = "${var.secrets_manager_teams_secret_paths[each.key]}/${local.secrets_manager_teams_postgres_migration_database_url_path}"
  recovery_window_in_days = 0

  depends_on = [
    postgresql_grant.teams_database[each.key],
    postgresql_grant.teams_schema[each.key],
    postgresql_grant.teams_table[each.key],
    postgresql_grant.teams_sequence[each.key],
    postgresql_grant.teams_migration_database[each.key],
    postgresql_grant.teams_migration_schema[each.key],
    postgresql_grant.teams_migration_table[each.key],
    postgresql_grant.teams_migration_sequence[each.key],
    postgresql_default_privileges.teams_future_tables[each.key],
    postgresql_default_privileges.teams_future_sequences[each.key],
  ]
}
resource "aws_secretsmanager_secret_version" "teams_postgres_migration_database_url" {
  for_each  = aws_secretsmanager_secret.teams_postgres_migration_database_url
  secret_id = each.value.id

  secret_string_wo         = "postgresql://${local.rds_postgres_teams_migration_usernames[each.key]}:${local.rds_postgres_teams_migration_passwords[each.key]}@${var.rds_postgres_local_host}:${var.rds_postgres_local_port}/${var.rds_postgres_db_name}"
  secret_string_wo_version = 1
}
# Allow teams to see that they have Postgres URI with credentials
resource "aws_ssm_parameter" "teams_postgres_migration_database_url" {
  for_each = aws_secretsmanager_secret.teams_postgres_migration_database_url
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/${local.secrets_manager_teams_postgres_migration_database_url_path}/secretsmanager/secret-id"
  type     = "String"
  value    = each.value.name

  depends_on = [
    aws_secretsmanager_secret_version.teams_postgres_migration_database_url[each.key]
  ]
}