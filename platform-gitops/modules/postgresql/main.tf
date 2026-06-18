locals {
  mle_schema_name = "mle"
}

# MLFLOW
resource "postgresql_schema" "mlflow" {
  name  = "mlflow"
  owner = var.db_owner_username
}
resource "postgresql_role" "mlflow" {
  name                = var.mlflow_db_username
  password            = var.mlflow_db_password
  login               = true
  connection_limit    = 20
  skip_reassign_owned = true
}
resource "postgresql_grant" "mlflow_database" {
  database    = var.db_name
  role        = postgresql_role.mlflow.name
  object_type = "database"
  privileges  = ["CONNECT"]
}
resource "postgresql_grant" "mlflow_schema" {
  database    = var.db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]
  depends_on  = [postgresql_schema.mlflow]
}
resource "postgresql_grant" "mlflow_table" {
  database    = var.db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
  depends_on  = [postgresql_schema.mlflow]
}
resource "postgresql_grant" "mlflow_sequence" {
  database    = var.db_name
  schema      = postgresql_schema.mlflow.name
  role        = postgresql_role.mlflow.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]
  depends_on  = [postgresql_schema.mlflow]
}

# MLE Applications
resource "postgresql_schema" "mle" {
  name  = local.mle_schema_name
  owner = var.db_owner_username
}
resource "postgresql_role" "mle" {
  name                = var.mle_db_username
  password            = var.mle_password
  login               = true
  connection_limit    = 50
  skip_reassign_owned = true
  search_path = [local.mle_schema_name]
}
resource "postgresql_grant" "mle_database" {
  database    = var.db_name
  role        = postgresql_role.mle.name
  object_type = "database"
  privileges  = ["CONNECT"]
}
resource "postgresql_grant" "mle_schema" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle.name
  object_type = "schema"
  privileges  = ["USAGE"]
  depends_on  = [postgresql_schema.mle]
}
resource "postgresql_grant" "mle_table" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  depends_on  = [postgresql_schema.mle]
}
resource "postgresql_grant" "mle_sequence" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]
  depends_on  = [postgresql_schema.mle]
}
# MLE Migrations
resource "postgresql_role" "mle_migration" {
  name                = var.mle_migrations_db_username
  password            = var.mle_migrations_db_password
  login               = true
  connection_limit    = 20
  skip_reassign_owned = true
  search_path = [local.mle_schema_name]
}
resource "postgresql_grant" "mle_migration_database" {
  database    = var.db_name
  role        = postgresql_role.mle_migration.name
  object_type = "database"
  privileges  = ["CONNECT"]
}
resource "postgresql_grant" "mle_migration_schema" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle_migration.name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]
  depends_on  = [postgresql_schema.mle]
}
resource "postgresql_grant" "mle_migration_table" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle_migration.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
  depends_on  = [postgresql_schema.mle]
}
resource "postgresql_grant" "mle_migration_sequence" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle_migration.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]
  depends_on  = [postgresql_schema.mle]
}

resource "postgresql_default_privileges" "mle_future_tables" {
  database    = var.db_name
  owner       = postgresql_role.mle_migration.name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  depends_on = [
    postgresql_schema.mle,
    postgresql_role.mle,
    postgresql_role.mle_migration
  ]
}
resource "postgresql_default_privileges" "mle_future_sequences" {
  database    = var.db_name
  owner       = postgresql_role.mle_migration.name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]
  depends_on = [
    postgresql_schema.mle,
    postgresql_role.mle,
    postgresql_role.mle_migration,
  ]
}