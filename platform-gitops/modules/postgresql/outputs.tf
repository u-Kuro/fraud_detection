output "mlflow_username" {
  value = postgresql_role.mlflow.name
  sensitive = true
}
output "mlflow_password" {
  value = postgresql_role.mlflow.password
  sensitive = true
}

output "team_usernames" {
  description = "Map of team name → PostgreSQL login role name"
  value       = { for k, v in postgresql_role.team : k => v.name }
  sensitive   = true
}

output "team_passwords" {
  description = "Map of team name → PostgreSQL login role password"
  value       = { for k, v in postgresql_role.team : k => v.password }
  sensitive   = true
}

output "team_migration_usernames" {
  description = "Map of team name → PostgreSQL migration role name"
  value       = { for k, v in postgresql_role.team_migration : k => v.name }
  sensitive   = true
}