# Create MLflow schema
resource "postgresql_schema" "mlflow" {
  name  = "mlflow"
  owner = var.rds_postgres_admin_username
}
# Create Postgres role for MLflow schema
resource "postgresql_role" "mlflow" {
  name                = var.rds_postgres_mlflow_username
  password            = var.rds_postgres_mlflow_password
  login               = true
  skip_reassign_owned = true
  search_path         = [postgresql_schema.mlflow.name]
}
# Grant MLflow permission to connect to the database
resource "postgresql_grant" "mlflow_database" {
  database    = var.rds_postgres_db_name
  role        = postgresql_role.mlflow.name
  object_type = "database"
  privileges  = ["CONNECT"]
}
# Grant MLflow full permission for its objects
resource "postgresql_grant" "mlflow_schema" {
  database    = var.rds_postgres_db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]
}
resource "postgresql_grant" "mlflow_table" {
  database    = var.rds_postgres_db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
}
resource "postgresql_grant" "mlflow_sequence" {
  database    = var.rds_postgres_db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]
}
# Create teams schemas
resource "postgresql_schema" "teams" {
  for_each = var.rds_postgres_teams
  name     = local.rds_postgres_teams_schemas[each.key]
  owner    = var.rds_postgres_admin_username
}
# Create Postgres roles for each teams' schema
resource "postgresql_role" "teams" {
  for_each            = var.rds_postgres_teams
  name                = local.rds_postgres_teams_usernames[each.key]
  password            = local.rds_postgres_teams_passwords[each.key] # Team can change it themselves (ALTER USER name WITH PASSWORD 'password')
  login               = true
  skip_reassign_owned = true
  search_path         = [postgresql_schema.teams[each.key].name]
}
# Grant teams permissions to connect to the database
resource "postgresql_grant" "teams_database" {
  for_each    = postgresql_role.teams
  database    = var.rds_postgres_db_name
  role        = each.value.name
  object_type = "database"
  privileges  = ["CONNECT"]
}
# Grant teams permissions to use objects in their schema
resource "postgresql_grant" "teams_schema" {
  for_each    = postgresql_schema.teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.teams[each.key].name
  object_type = "schema"
  privileges  = ["USAGE"]
}
resource "postgresql_grant" "teams_table" {
  for_each    = postgresql_schema.teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.teams[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
}
resource "postgresql_grant" "teams_sequence" {
  for_each    = postgresql_schema.teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.teams[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]
}
# Create Postgres roles for each teams' schema for migration
resource "postgresql_role" "teams_migration" {
  for_each            = var.rds_postgres_teams
  name                = local.rds_postgres_teams_migration_usernames[each.key]
  password            = local.rds_postgres_teams_migration_passwords[each.key] # Team can change it themselves (ALTER USER name WITH PASSWORD 'password')
  login               = true
  skip_reassign_owned = true
  search_path         = [postgresql_schema.teams[each.key].name]
}
# Grant teams' migration roles permissions to connect to the database
resource "postgresql_grant" "teams_migration_database" {
  for_each    = postgresql_role.teams_migration
  database    = var.rds_postgres_db_name
  role        = each.value.name
  object_type = "database"
  privileges  = ["CONNECT"]
}
# Grant teams permissions to manage objects in their schema
resource "postgresql_grant" "teams_migration_schema" {
  for_each    = postgresql_schema.teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.teams_migration[each.key].name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]
}
resource "postgresql_grant" "teams_migration_table" {
  for_each    = postgresql_schema.teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.teams_migration[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
}
resource "postgresql_grant" "teams_migration_sequence" {
  for_each    = postgresql_schema.teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  role        = postgresql_role.teams_migration[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]
}
# Grant teams permissions for future objects in their schema
resource "postgresql_default_privileges" "teams_future_tables" {
  for_each    = postgresql_schema.teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  owner       = postgresql_role.teams_migration[each.key].name
  role        = postgresql_role.teams[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
}
resource "postgresql_default_privileges" "teams_future_sequences" {
  for_each    = postgresql_schema.teams
  database    = var.rds_postgres_db_name
  schema      = each.value.name
  owner       = postgresql_role.teams_migration[each.key].name
  role        = postgresql_role.teams[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]
}