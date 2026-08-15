# RDS (Postgres)
# /mlflow
output "mlflow_username" {
  value     = postgresql_role.mlflow.name
  sensitive = true
}
output "mlflow_password" {
  value     = postgresql_role.mlflow.password
  sensitive = true
}
# /teams
output "teams_usernames" {
  value = local.rds_postgres_teams_usernames
  sensitive = true
}
output "teams_passwords" {
  value = local.rds_postgres_teams_passwords
  sensitive = true
}
output "teams_migration_usernames" {
  value = local.rds_postgres_teams_migration_usernames
  sensitive = true
}
output "teams_migration_passwords" {
  value = local.rds_postgres_teams_migration_passwords
  sensitive = true
}