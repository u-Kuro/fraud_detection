# MLFLOW
resource "postgresql_schema" "mlflow" {
  name  = "mlflow"
  owner = var.db_owner_username
}
resource "postgresql_role" "mlflow" {
  name                = var.mlflow_postgresql_username
  password            = var.mlflow_postgresql_password
  login               = true
  skip_reassign_owned = true
  search_path         = [postgresql_schema.mlflow.name]
}
resource "postgresql_grant" "mlflow_database" {
  database    = var.db_name
  role        = postgresql_role.mlflow.name
  object_type = "database"
  privileges  = ["CONNECT"]
  depends_on  = [postgresql_role.mlflow]
}
resource "postgresql_grant" "mlflow_schema" {
  database    = var.db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]
  depends_on  = [
    postgresql_schema.mlflow,
    postgresql_role.mlflow
  ]
}
resource "postgresql_grant" "mlflow_table" {
  database    = var.db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
  depends_on  = [
    postgresql_schema.mlflow,
    postgresql_role.mlflow
  ]
}
resource "postgresql_grant" "mlflow_sequence" {
  database    = var.db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]
  depends_on  = [
    postgresql_schema.mlflow,
    postgresql_role.mlflow
  ]
}

# MLE (/dags and /services)
resource "random_password" "teams" {
  for_each  = var.postgresql_teams
  length    = 24
}
resource "postgresql_schema" "teams" {
  for_each  = random_password.teams
  name      = each.key
  owner     = var.db_owner_username
}
resource "postgresql_role" "teams" {
  for_each            = random_password.teams
  name                = each.key
  password            = each.value.result
  login               = true
  skip_reassign_owned = true
  search_path         = [postgresql_schema.teams[each.key].name]
}
resource "postgresql_grant" "teams_database" {
  for_each    = postgresql_role.teams
  database    = var.db_name
  role        = each.value.name
  object_type = "database"
  privileges  = ["CONNECT"]
  depends_on  = [postgresql_role.teams]
}
resource "postgresql_grant" "teams_schema" {
  for_each    = postgresql_schema.teams
  database    = var.db_name
  schema      = each.value.name
  role        = postgresql_role.teams[each.key].name
  object_type = "schema"
  privileges  = ["USAGE"]
  depends_on  = [
    postgresql_schema.teams,
    postgresql_role.teams
  ]
}
resource "postgresql_grant" "teams_table" {
  for_each    = postgresql_schema.teams
  database    = var.db_name
  schema      = each.value.name
  role        = postgresql_role.teams[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  depends_on  = [
    postgresql_schema.teams,
    postgresql_role.teams
  ]
}
resource "postgresql_grant" "teams_sequence" {
  for_each    = postgresql_schema.teams
  database    = var.db_name
  schema      = each.value.name
  role        = postgresql_role.teams[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]
  depends_on  = [
    postgresql_schema.teams,
    postgresql_role.teams
  ]
}
# MLE Migrations (/database)
resource "random_password" "teams_migration" {
  for_each  = var.postgresql_teams
  length    = 24
}
resource "postgresql_role" "teams_migration" {
  for_each            = random_password.teams_migration
  name                = each.key
  password            = each.value.result
  login               = true
  skip_reassign_owned = true
  search_path         = [postgresql_schema.teams[each.key].name]
}
resource "postgresql_grant" "teams_migration_database" {
  for_each    = postgresql_role.teams_migration
  database    = var.db_name
  role        = each.value.name
  object_type = "database"
  privileges  = ["CONNECT"]
  depends_on  = [postgresql_role.teams_migration]
}
resource "postgresql_grant" "teams_migration_schema" {
  for_each    = postgresql_schema.teams
  database    = var.db_name
  schema      = each.value.name
  role        = postgresql_role.teams_migration[each.key].name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]
  depends_on  = [
    postgresql_schema.teams,
    postgresql_role.teams_migration
  ]
}
resource "postgresql_grant" "mle_migration_table" {
  for_each    = postgresql_schema.teams
  database    = var.db_name
  schema      = each.value.name
  role        = postgresql_role.teams_migration[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
  depends_on  = [
    postgresql_schema.teams,
    postgresql_role.teams_migration
  ]
}
resource "postgresql_grant" "mle_migration_sequence" {
  for_each    = postgresql_schema.teams
  database    = var.db_name
  schema      = each.value.name
  role        = postgresql_role.teams_migration[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]
  depends_on  = [
    postgresql_schema.teams,
    postgresql_role.teams_migration
  ]
}

resource "postgresql_default_privileges" "mle_future_tables" {
  for_each    = postgresql_schema.teams
  database    = var.db_name
  schema      = each.value.name
  owner       = postgresql_role.teams_migration[each.key].name
  role        = postgresql_role.teams[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  depends_on  = [
    postgresql_schema.teams,
    postgresql_role.teams_migration,
    postgresql_role.teams
  ]
}
resource "postgresql_default_privileges" "mle_future_sequences" {
  for_each    = postgresql_schema.teams
  database    = var.db_name
  schema      = each.value.name
  owner       = postgresql_role.teams_migration[each.key].name
  role        = postgresql_role.teams[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]
  depends_on  = [
    postgresql_schema.teams,
    postgresql_role.teams_migration,
    postgresql_role.teams
  ]
}