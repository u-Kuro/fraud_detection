output "mlflow_username" {
  value = postgresql_role.mlflow.name
  sensitive = true
}
output "mlflow_password" {
  value = postgresql_role.mlflow.password
  sensitive = true
}

output "mle_username" {
  value = postgresql_role.mle.name
  sensitive = true
}
output "mle_password" {
  value = postgresql_role.mle.password
  sensitive = true
}

output "mle_migration_username" {
  value = postgresql_role.mle_migration.name
  sensitive = true
}
output "mle_migration_password" {
  value = postgresql_role.mle_migration.password
  sensitive = true
}