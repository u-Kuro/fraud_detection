# Create MLflow schema
resource "postgresql_schema" "mlflow" {
  name  = "mlflow"
  owner = var.rds_postgres_username
}
# Create Postgres role for MLflow schema
resource "postgresql_role" "mlflow" {
  name                = var.rds_postgres_mlflow_username
  password            = var.rds_postgres_mlflow_password
  login               = true
  skip_reassign_owned = true
  search_path         = postgresql_schema.mlflow.name

  depends_on = [postgresql_schema.mlflow]
}
# Grant MLflow permission to connect to the database
resource "postgresql_grant" "mlflow_database" {
  database    = var.rds_postgres_db_name
  role        = postgresql_role.mlflow.name
  object_type = "database"
  privileges  = ["CONNECT"]

  depends_on = [postgresql_role.mlflow]
}
# Grant MLflow full permission for its objects
resource "postgresql_grant" "mlflow_schema" {
  database    = var.rds_postgres_db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]

  depends_on = [
    postgresql_schema.mlflow,
    postgresql_role.mlflow
  ]
}
resource "postgresql_grant" "mlflow_table" {
  database    = var.rds_postgres_db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]

  depends_on = [
    postgresql_schema.mlflow,
    postgresql_role.mlflow
  ]
}
resource "postgresql_grant" "mlflow_sequence" {
  database    = var.rds_postgres_db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]

  depends_on = [
    postgresql_schema.mlflow,
    postgresql_role.mlflow
  ]
}
# TODO - NEEDS TO SAVE CREDENTIALS TO SECRETSMANAGER (only teams not migration for k8s since atlas does not run there)
# Create teams schemas
resource "postgresql_schema" "postgresql_teams" {
  for_each = var.rds_postgres_teams
  name     = local.rds_postgres_teams_schemas[each.key]
  owner    = var.rds_postgres_username
}
# Create Postgres roles for each teams' schema
resource "postgresql_role" "postgresql_teams" {
  for_each            = var.rds_postgres_teams
  name                = local.rds_postgres_teams_usernames[each.key]
  password            = local.rds_postgres_teams_passwords[each.key] # Team can change it themselves (ALTER USER name WITH PASSWORD 'password')
  login               = true
  skip_reassign_owned = true
  search_path         = postgresql_schema.postgresql_teams[each.key].name

  depends_on = [postgresql_schema.postgresql_teams]
}
# Grant teams permissions to connect to the database
resource "postgresql_grant" "postgresql_teams_database" {
  for_each    = postgresql_role.postgresql_teams
  database    = var.rds_postgres_db_name
  role        = each.value.name
  object_type = "database"
  privileges  = ["CONNECT"]

  depends_on = [postgresql_role.postgresql_teams]
}
# Grant teams permissions to use objects in their schema
resource "postgresql_grant" "postgresql_teams_schema" {
  for_each    = postgresql_schema.postgresql_teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.postgresql_teams[each.key].name
  object_type = "schema"
  privileges  = ["USAGE"]

  depends_on = [
    postgresql_schema.postgresql_teams,
    postgresql_role.postgresql_teams
  ]
}
resource "postgresql_grant" "postgresql_teams_table" {
  for_each    = postgresql_schema.postgresql_teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.postgresql_teams[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]

  depends_on = [
    postgresql_schema.postgresql_teams,
    postgresql_role.postgresql_teams
  ]
}
resource "postgresql_grant" "postgresql_teams_sequence" {
  for_each    = postgresql_schema.postgresql_teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.postgresql_teams[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]

  depends_on = [
    postgresql_schema.postgresql_teams,
    postgresql_role.postgresql_teams
  ]
}
# Create Postgres roles for each teams' schema for migration
resource "postgresql_role" "postgresql_teams_migration" {
  for_each            = var.rds_postgres_teams
  name                = local.rds_postgres_teams_migration_usernames[each.key]
  password            = local.rds_postgres_teams_migration_passwords[each.key] # Team can change it themselves (ALTER USER name WITH PASSWORD 'password')
  login               = true
  skip_reassign_owned = true
  search_path         = postgresql_schema.postgresql_teams[each.key].name

  depends_on = [postgresql_schema.postgresql_teams]
}
# Grant teams' migration roles permissions to connect to the database
resource "postgresql_grant" "postgresql_teams_migration_database" {
  for_each    = postgresql_role.postgresql_teams_migration
  database    = var.rds_postgres_db_name
  role        = each.value.name
  object_type = "database"
  privileges  = ["CONNECT"]

  depends_on = [postgresql_role.postgresql_teams_migration]
}
# Grant teams permissions to manage objects in their schema
resource "postgresql_grant" "postgresql_teams_migration_schema" {
  for_each    = postgresql_schema.postgresql_teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.postgresql_teams_migration[each.key].name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]

  depends_on = [
    postgresql_schema.postgresql_teams,
    postgresql_role.postgresql_teams_migration
  ]
}
resource "postgresql_grant" "postgresql_teams_migration_table" {
  for_each    = postgresql_schema.postgresql_teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.postgresql_teams_migration[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]

  depends_on = [
    postgresql_schema.postgresql_teams,
    postgresql_role.postgresql_teams_migration
  ]
}
resource "postgresql_grant" "postgresql_teams_migration_sequence" {
  for_each    = postgresql_schema.postgresql_teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.postgresql_teams_migration[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]

  depends_on = [
    postgresql_schema.postgresql_teams,
    postgresql_role.postgresql_teams_migration
  ]
}
# Grant teams permissions for future objects in their schema
resource "postgresql_default_privileges" "postgresql_teams_future_tables" {
  for_each    = postgresql_schema.postgresql_teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  owner       = postgresql_role.postgresql_teams_migration[each.key].name
  role        = postgresql_role.postgresql_teams[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]

  depends_on = [
    postgresql_schema.postgresql_teams,
    postgresql_role.postgresql_teams_migration,
    postgresql_role.postgresql_teams
  ]
}
resource "postgresql_default_privileges" "postgresql_teams_future_sequences" {
  for_each    = postgresql_schema.postgresql_teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  owner       = postgresql_role.postgresql_teams_migration[each.key].name
  role        = postgresql_role.postgresql_teams[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]

  depends_on = [
    postgresql_schema.postgresql_teams,
    postgresql_role.postgresql_teams_migration,
    postgresql_role.postgresql_teams
  ]
}