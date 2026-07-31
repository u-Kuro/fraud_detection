# MLFLOW
locals {
  mlflow_schema_name = "mlflow"
}
resource "postgresql_schema" "mlflow" {
  name  = local.mlflow_schema_name
  owner = var.db_owner_username
}
resource "postgresql_role" "mlflow" {
  name                = var.mlflow_postgresql_username
  password            = var.mlflow_postgresql_password
  login               = true
  skip_reassign_owned = true
  search_path         = [local.mlflow_schema_name]
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
locals {
  mle_schema_name = "mle"
}
resource "postgresql_schema" "mle" {
  name  = local.mle_schema_name
  owner = var.db_owner_username
}
resource "postgresql_role" "mle" {
  name                = var.mle_postgresql_username
  password            = var.mle_postgresql_password
  login               = true
  skip_reassign_owned = true
  search_path         = [local.mle_schema_name]
}
resource "postgresql_grant" "mle_database" {
  database    = var.db_name
  role        = postgresql_role.mle.name
  object_type = "database"
  privileges  = ["CONNECT"]
  depends_on  = [postgresql_role.mle]
}
resource "postgresql_grant" "mle_schema" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle.name
  object_type = "schema"
  privileges  = ["USAGE"]
  depends_on  = [
    postgresql_schema.mle,
    postgresql_role.mle
  ]
}
resource "postgresql_grant" "mle_table" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  depends_on  = [
    postgresql_schema.mle,
    postgresql_role.mle
  ]
}
resource "postgresql_grant" "mle_sequence" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]
  depends_on  = [
    postgresql_schema.mle,
    postgresql_role.mle
  ]
}
# MLE Migrations (/database)
resource "postgresql_role" "mle_migration" {
  name                = var.mle_migrations_postgresql_username
  password            = var.mle_migrations_postgresql_password
  login               = true
  skip_reassign_owned = true
  search_path         = [local.mle_schema_name]
}
resource "postgresql_grant" "mle_migration_database" {
  database    = var.db_name
  role        = postgresql_role.mle_migration.name
  object_type = "database"
  privileges  = ["CONNECT"]
  depends_on  = [postgresql_role.mle_migration]
}
resource "postgresql_grant" "mle_migration_schema" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle_migration.name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]
  depends_on  = [
    postgresql_schema.mle,
    postgresql_role.mle_migration
  ]
}
resource "postgresql_grant" "mle_migration_table" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle_migration.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
  depends_on  = [
    postgresql_schema.mle,
    postgresql_role.mle_migration
  ]
}
resource "postgresql_grant" "mle_migration_sequence" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  role        = postgresql_role.mle_migration.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]
  depends_on  = [
    postgresql_schema.mle,
    postgresql_role.mle_migration
  ]
}

resource "postgresql_default_privileges" "mle_future_tables" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  owner       = postgresql_role.mle_migration.name
  role        = postgresql_role.mle.name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  depends_on  = [
    postgresql_schema.mle,
    postgresql_role.mle_migration,
    postgresql_role.mle
  ]
}
resource "postgresql_default_privileges" "mle_future_sequences" {
  database    = var.db_name
  schema      = postgresql_schema.mle.name
  owner       = postgresql_role.mle_migration.name
  role        = postgresql_role.mle.name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]
  depends_on  = [
    postgresql_schema.mle,
    postgresql_role.mle_migration,
    postgresql_role.mle,
  ]
}