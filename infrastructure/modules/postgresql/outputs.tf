output "mlflow_username" {
  value     = postgresql_role.mlflow.name
  sensitive = true
}
output "mlflow_password" {
  value     = postgresql_role.mlflow.password
  sensitive = true
}

output "users" {
  value = {
    teams = {
      for k, v in postgresql_role.postgresql_teams : k => {
        password = v.password
        username = v.name
      }
    }
  }
  sensitive = true
}
output "teams_migration_credentials" {
  value = {
    for k, v in random_password.teams_migration
    : k => v.result
  }
  sensitive = true
}