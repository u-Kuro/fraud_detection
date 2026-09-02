# AWS
# /admin
variable "aws_admin_access_key" {
  type      = string
  sensitive = true
}
variable "aws_admin_secret_key" {
  type      = string
  sensitive = true
}
variable "aws_admin_region" { type = string }
variable "aws_admin_account_id" { type = string }

# RDS
# /postgres
variable "rds_postgres_admin_username" {
  type      = string
  sensitive = true
  default   = "admin" # Can't be changed in MiniStack's RDS
}
variable "rds_postgres_admin_password" {
  type      = string
  sensitive = true
  default   = "admin" # Can't be changed in MiniStack's RDS
}
# /mlflow-schema
variable "rds_postgres_mlflow_username" {
  type      = string
  sensitive = true
}
variable "rds_postgres_mlflow_password" {
  type      = string
  sensitive = true
}

# MLflow
# /admin
variable "mlflow_admin_username" {
  type      = string
  sensitive = true
}
variable "mlflow_admin_password" {
  type      = string
  sensitive = true
}
# /app-secret-key
variable "mlflow_flask_server_secret_key" {
  type      = string
  sensitive = true
}

# sslip.io
# /dns
variable "sslip_io_public_wildcard_dns_domain" {
  type    = string
  default = "sslip.io"
}