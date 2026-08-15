# RDS
# /postgres
variable "rds_postgres_username" {
  type      = string
  sensitive = true
}
variable "rds_postgres_db_name" { type = string }
# /mlflow-schema
variable "rds_postgres_mlflow_username" {
  type      = string
  sensitive = true
}
variable "rds_postgres_mlflow_password" {
  type      = string
  sensitive = true
}
# /teams
variable "rds_postgres_teams" { type = set(string) }

# Secrets Manager
# /teams
variable "secrets_manager_teams_secret_paths" { type = map(string) }

# SSM
# /teams
variable "ssm_teams_parameter_paths" { type = map(string) }