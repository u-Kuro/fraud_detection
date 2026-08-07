# MLFLOW
resource "postgresql_schema" "mlflow" {
  name  = "mlflow"
  owner = var.rds.username
}
resource "postgresql_role" "mlflow" {
  name                = var.rds.users.mlflow.username
  password            = var.rds.users.mlflow.password
  login               = true
  skip_reassign_owned = true
  search_path         = postgresql_schema.mlflow.name

  depends_on = [postgresql_schema.mlflow]
}
resource "postgresql_grant" "mlflow_database" {
  database    = var.rds.db_name
  role        = postgresql_role.mlflow.name
  object_type = "database"
  privileges  = ["CONNECT"]

  depends_on  = [postgresql_role.mlflow]
}
resource "postgresql_grant" "mlflow_schema" {
  database    = var.rds.db_name
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
  database    = var.rds.db_name
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
  database    = var.rds.db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]

  depends_on = [
    postgresql_schema.mlflow,
    postgresql_role.mlflow
  ]
}
# TEAMS
resource "postgresql_schema" "teams" {
  for_each = var.aws.users.postgresql_teams
  name     = each.value
  owner    = var.rds.username
}
resource "postgresql_role" "teams" {
  for_each            = var.aws.users.postgresql_teams
  name                = each.value
  password            = each.value # Team can change it themselves (ALTER USER name WITH PASSWORD 'password')
  login               = true
  skip_reassign_owned = true
  search_path         = postgresql_schema.teams[each.value].name

  depends_on = [postgresql_schema.teams]
}
resource "postgresql_grant" "teams_database" {
  for_each    = postgresql_role.teams
  database    = var.rds.db_name
  role        = each.value.name
  object_type = "database"
  privileges  = ["CONNECT"]

  depends_on  = [postgresql_role.teams]
}
resource "postgresql_grant" "teams_schema" {
  for_each    = postgresql_schema.teams
  database    = var.rds.db_name
  schema      = each.value.name
  role        = postgresql_role.teams[each.value].name
  object_type = "schema"
  privileges  = ["USAGE"]

  depends_on = [
    postgresql_schema.teams,
    postgresql_role.teams
  ]
}
resource "postgresql_grant" "teams_table" {
  for_each    = postgresql_schema.teams
  database    = var.rds.db_name
  schema      = each.value.name
  role        = postgresql_role.teams[each.value].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]

  depends_on = [
    postgresql_schema.teams,
    postgresql_role.teams
  ]
}
resource "postgresql_grant" "teams_sequence" {
  for_each    = postgresql_schema.teams
  database    = var.rds.db_name
  schema      = each.value.name
  role        = postgresql_role.teams[each.value].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]

  depends_on = [
    postgresql_schema.teams,
    postgresql_role.teams
  ]
}
# TEAM MIGRATIONS
resource "postgresql_role" "teams_migration" {
  for_each            = var.aws.users.postgresql_teams
  name                = "${each.value}_migration"
  password            = "${each.value}_migration" # Team can change it themselves (ALTER USER name WITH PASSWORD 'password')
  login               = true
  skip_reassign_owned = true
  search_path         = postgresql_schema.teams[each.value].name

  depends_on = [postgresql_schema.teams]
}
resource "postgresql_grant" "teams_migration_database" {
  for_each    = postgresql_role.teams_migration
  database    = var.rds.db_name
  role        = each.value.name
  object_type = "database"
  privileges  = ["CONNECT"]

  depends_on  = [postgresql_role.teams_migration]
}
resource "postgresql_grant" "teams_migration_schema" {
  for_each    = postgresql_schema.teams
  database    = var.rds.db_name
  schema      = each.value.name
  role        = postgresql_role.teams_migration[each.value].name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]

  depends_on = [
    postgresql_schema.teams,
    postgresql_role.teams_migration
  ]
}
resource "postgresql_grant" "teams_migration_table" {
  for_each    = postgresql_schema.teams
  database    = var.rds.db_name
  schema      = each.value.name
  role        = postgresql_role.teams_migration[each.value].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]

  depends_on = [
    postgresql_schema.teams,
    postgresql_role.teams_migration
  ]
}
resource "postgresql_grant" "teams_migration_sequence" {
  for_each    = postgresql_schema.teams
  database    = var.rds.db_name
  schema      = each.value.name
  role        = postgresql_role.teams_migration[each.value].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]

  depends_on = [
    postgresql_schema.teams,
    postgresql_role.teams_migration
  ]
}
# TEAM DEFAULT PRIVILEGES
resource "postgresql_default_privileges" "teams_future_tables" {
  for_each    = postgresql_schema.teams
  database    = var.rds.db_name
  schema      = each.value.name
  owner       = postgresql_role.teams_migration[each.value].name
  role        = postgresql_role.teams[each.value].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]

  depends_on = [
    postgresql_schema.teams,
    postgresql_role.teams_migration,
    postgresql_role.teams
  ]
}
resource "postgresql_default_privileges" "teams_future_sequences" {
  for_each    = postgresql_schema.teams
  database    = var.rds.db_name
  schema      = each.value.name
  owner       = postgresql_role.teams_migration[each.value].name
  role        = postgresql_role.teams[each.value].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]

  depends_on = [
    postgresql_schema.teams,
    postgresql_role.teams_migration,
    postgresql_role.teams
  ]
}