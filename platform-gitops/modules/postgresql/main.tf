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

# ── Per-team schema + login role ───────────────────────────────────────────────
locals {
  teams_with_pg = { for k, v in var.teams : k => v if v.pg_schema != null }
  teams_with_migrations = {
    for k, v in var.teams : k => v
    if v.pg_migrations_username != null
  }
}

resource "postgresql_schema" "team" {
  for_each = local.teams_with_pg
  name     = each.value.pg_schema
  owner    = var.db_owner_username
}

resource "postgresql_role" "team" {
  for_each            = local.teams_with_pg
  name                = each.value.pg_username
  password            = each.value.pg_password
  login               = true
  skip_reassign_owned = true
  search_path         = [each.value.pg_schema]
}

resource "postgresql_grant" "team_database" {
  for_each    = local.teams_with_pg
  database    = var.db_name
  role        = postgresql_role.team[each.key].name
  object_type = "database"
  privileges  = ["CONNECT"]
  depends_on  = [postgresql_role.team]
}

resource "postgresql_grant" "team_schema_usage" {
  for_each    = local.teams_with_pg
  database    = var.db_name
  schema      = postgresql_schema.team[each.key].name
  role        = postgresql_role.team[each.key].name
  object_type = "schema"
  privileges  = ["USAGE"]
  depends_on  = [postgresql_schema.team, postgresql_role.team]
}

resource "postgresql_grant" "team_table" {
  for_each    = local.teams_with_pg
  database    = var.db_name
  schema      = postgresql_schema.team[each.key].name
  role        = postgresql_role.team[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  depends_on  = [postgresql_schema.team, postgresql_role.team]
}

resource "postgresql_grant" "team_sequence" {
  for_each    = local.teams_with_pg
  database    = var.db_name
  schema      = postgresql_schema.team[each.key].name
  role        = postgresql_role.team[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]
  depends_on  = [postgresql_schema.team, postgresql_role.team]
}

# ── Migration roles (CREATE on schema + default privileges forward grant) ──────
resource "postgresql_role" "team_migration" {
  for_each            = local.teams_with_migrations
  name                = each.value.pg_migrations_username
  password            = each.value.pg_migrations_password
  login               = true
  skip_reassign_owned = true
  search_path         = [each.value.pg_schema]
}

resource "postgresql_grant" "team_migration_database" {
  for_each    = local.teams_with_migrations
  database    = var.db_name
  role        = postgresql_role.team_migration[each.key].name
  object_type = "database"
  privileges  = ["CONNECT"]
  depends_on  = [postgresql_role.team_migration]
}

resource "postgresql_grant" "team_migration_schema" {
  for_each    = local.teams_with_migrations
  database    = var.db_name
  schema      = postgresql_schema.team[each.key].name
  role        = postgresql_role.team_migration[each.key].name
  object_type = "schema"
  privileges  = ["USAGE", "CREATE"]
  depends_on  = [postgresql_schema.team, postgresql_role.team_migration]
}

resource "postgresql_grant" "team_migration_table" {
  for_each    = local.teams_with_migrations
  database    = var.db_name
  schema      = postgresql_schema.team[each.key].name
  role        = postgresql_role.team_migration[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE", "REFERENCES", "TRIGGER"]
  depends_on  = [postgresql_schema.team, postgresql_role.team_migration]
}

resource "postgresql_grant" "team_migration_sequence" {
  for_each    = local.teams_with_migrations
  database    = var.db_name
  schema      = postgresql_schema.team[each.key].name
  role        = postgresql_role.team_migration[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT", "UPDATE"]
  depends_on  = [postgresql_schema.team, postgresql_role.team_migration]
}

# Forward-grant: objects created by the migration role are readable by the base role.
resource "postgresql_default_privileges" "team_future_tables" {
  for_each    = local.teams_with_migrations
  database    = var.db_name
  schema      = postgresql_schema.team[each.key].name
  owner       = postgresql_role.team_migration[each.key].name
  role        = postgresql_role.team[each.key].name
  object_type = "table"
  privileges  = ["SELECT", "INSERT", "UPDATE", "DELETE"]
  depends_on  = [postgresql_schema.team, postgresql_role.team_migration, postgresql_role.team]
}

resource "postgresql_default_privileges" "team_future_sequences" {
  for_each    = local.teams_with_migrations
  database    = var.db_name
  schema      = postgresql_schema.team[each.key].name
  owner       = postgresql_role.team_migration[each.key].name
  role        = postgresql_role.team[each.key].name
  object_type = "sequence"
  privileges  = ["USAGE", "SELECT"]
  depends_on  = [postgresql_schema.team, postgresql_role.team_migration, postgresql_role.team]
}