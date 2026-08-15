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