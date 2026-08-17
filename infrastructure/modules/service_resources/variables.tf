# IAM
# /admin
variable "iam_admin_region" { type = string }
# /teams
variable "iam_teams_usernames" {
  type      = map(string)
  sensitive = true
}
variable "iam_teams_passwords" {
  type      = map(string)
  sensitive = true
}

# ECR
# /aws
variable "ecr_aws_endpoint" { type = string }
variable "ecr_aws_authorization_token" {
  type      = string
  sensitive = true
}
variable "ecr_aws_authorization_token_username" {
  type      = string
  sensitive = true
}
variable "ecr_aws_authorization_token_password" {
  type      = string
  sensitive = true
}

# EKS
# /teams
variable "eks_teams" { type = set(string) }
variable "eks_teams_kubernetes_namespaces" { type = map(string) }

# MLflow
# /urls
variable "mlflow_ingress_url" { type = string }
variable "mlflow_inter_url" { type = string }
# /teams
variable "mlflow_teams" { type = set(string) }
variable "mlflow_teams_usernames" {
  type      = map(string)
  sensitive = true
}
variable "mlflow_teams_passwords" {
  type      = map(string)
  sensitive = true
}

# MWAA
# /urls
variable "mwaa_url" { type = string }
# /teams
variable "mwaa_teams" { type = set(string) }
variable "mwaa_teams_environment_names" { type = map(string) }
variable "mwaa_teams_connections_prefixes" { type = map(string) }
variable "mwaa_teams_variables_prefixes" { type = map(string) }

# RDS
# /postgres
variable "rds_postgres_host" { type = string }
variable "rds_postgres_port" { type = number }
variable "rds_postgres_db_name" { type = string }
# /teams
variable "rds_postgres_teams" { type = set(string) }
variable "rds_postgres_teams_usernames" {
  type      = map(string)
  sensitive = true
}
variable "rds_postgres_teams_passwords" {
  type      = map(string)
  sensitive = true
}

# S3
# /urls
variable "s3_url" { type = string }
# /teams
variable "s3_teams" { type = set(string) }