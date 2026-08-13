# MLFLOW
resource "postgresql_schema" "mlflow" {
  name  = "MLFLOW"
  owner = local.rds.username
}
resource "postgresql_role" "mlflow" {
  name                = local.rds.users.mlflow.username
  password            = local.rds.users.mlflow.password
  login               = true
  skip_reassign_owned = true
  search_path         = postgresql_schema.mlflow.name

  depends_on = [postgresql_schema.mlflow]
}
resource "postgresql_grant" "mlflow_database" {
  database    = local.rds.db_name
  role        = postgresql_role.mlflow.name
  object_type = "database"
  privileges  = ["CONNECT"]

  depends_on = [postgresql_role.mlflow]
}
resource "postgresql_grant" "mlflow_schema" {
  database    = local.rds.db_name
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
  database    = local.rds.db_name
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
  database    = local.rds.db_name
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
# POSTGRESQL TEAMS
resource "postgresql_schema" "postgresql_teams" {
  for_each = local.rds.users.teams
  name     = each.key
  owner    = local.rds.username
}
resource "postgresql_role" "postgresql_teams" {
  for_each            = local.rds.users.teams
  name                = each.key
  password            = each.key # Team can change it themselves (ALTER USER name WITH PASSWORD 'password')
  login               = true
  skip_reassign_owned = true
  search_path         = postgresql_schema.postgresql_teams[each.key].name

  depends_on = [postgresql_schema.postgresql_teams]
}
resource "postgresql_grant" "postgresql_teams_database" {
  for_each    = postgresql_role.postgresql_teams
  database    = local.rds.db_name
  role        = each.value.name
  object_type = "database"
  privileges  = ["CONNECT"]

  depends_on = [postgresql_role.postgresql_teams]
}
resource "postgresql_grant" "postgresql_teams_schema" {
  for_each    = postgresql_schema.postgresql_teams
  database    = local.rds.db_name
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
  database    = local.rds.db_name
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
  database    = local.rds.db_name
  schema      = each.value.name
  role        = postgresql_role.postgresql_teams[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]

  depends_on = [
    postgresql_schema.postgresql_teams,
    postgresql_role.postgresql_teams
  ]
}
# POSTGRESQL TEAMS' MIGRATIONS
resource "postgresql_role" "postgresql_teams_migration" {
  for_each            = local.rds.users.teams
  name                = "${each.key}_MIGRATION"
  password            = "${each.key}_MIGRATION" # Team can change it themselves (ALTER USER name WITH PASSWORD 'password')
  login               = true
  skip_reassign_owned = true
  search_path         = postgresql_schema.postgresql_teams[each.key].name

  depends_on = [postgresql_schema.postgresql_teams]
}
resource "postgresql_grant" "postgresql_teams_migration_database" {
  for_each    = postgresql_role.postgresql_teams_migration
  database    = local.rds.db_name
  role        = each.value.name
  object_type = "database"
  privileges  = ["CONNECT"]

  depends_on = [postgresql_role.postgresql_teams_migration]
}
resource "postgresql_grant" "postgresql_teams_migration_schema" {
  for_each    = postgresql_schema.postgresql_teams
  database    = local.rds.db_name
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
  database    = local.rds.db_name
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
  database    = local.rds.db_name
  schema      = each.value.name
  role        = postgresql_role.postgresql_teams_migration[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]

  depends_on = [
    postgresql_schema.postgresql_teams,
    postgresql_role.postgresql_teams_migration
  ]
}
# POSTGRESQL TEAMS' DEFAULT PRIVILEGES
resource "postgresql_default_privileges" "postgresql_teams_future_tables" {
  for_each    = postgresql_schema.postgresql_teams
  database    = local.rds.db_name
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
  database    = local.rds.db_name
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