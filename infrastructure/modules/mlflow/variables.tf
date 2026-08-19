# IAM
# /admin
variable "iam_admin_username" {
  type      = string
  sensitive = true
}
variable "iam_admin_password" {
  type      = string
  sensitive = true
}
variable "iam_admin_region" { type = string }

# EKS
# /domain
variable "eks_ingress_domain" { type = string }
variable "eks_ingress_domain_from_host" { type = string }
# /mlflow
variable "eks_mlflow_namespace" {
  type    = string
  default = "mlflow"
}

# MLflow
# /deployment
variable "mlflow_host" {
  type    = string
  default = "mlflow"
}
variable "mlflow_container_port" {
  type    = number
  default = 8080
}
variable "mlflow_flask_server_secret_key" {
  type      = string
  sensitive = true
}
variable "mlflow_admin_username" {
  type      = string
  sensitive = true
}
variable "mlflow_admin_password" {
  type      = string
  sensitive = true
}
# /teams
variable "mlflow_teams" { type = set(string) }

# RDS
# /postgres
variable "rds_postgres_db_name" { type = string }
variable "rds_postgres_host" { type = string }
variable "rds_postgres_port" { type = number }
# /mlflow-schema
variable "rds_postgres_mlflow_username" {
  type      = string
  sensitive = true
}
variable "rds_postgres_mlflow_password" {
  type      = string
  sensitive = true
}

# S3
# /urls
variable "s3_url" { type = string }
variable "s3_mlflow_bucket_name" { type = string }
variable "s3_mlflow_bucket_arn" { type = string }

# Secrets Manager
# /teams
variable "secrets_manager_teams_secret_paths" { type = map(string) }

# SSM
# /teams
variable "ssm_teams_parameter_paths" { type = map(string) }

# Traefik
# /entry-point
variable "traefik_eks_host_entry_point" {type = string}
# /port
variable "traefik_http_port" {
  type    = number
  default = 80
}