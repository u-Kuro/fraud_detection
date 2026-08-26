# IAM
# /services
variable "iam_rds_role_name" { type = string }

# Ministack
# /network
variable "ministack_network_name" { type = string }

# RDS
# /service
# /postgres
variable "rds_postgres_admin_username" {
  type      = string
  sensitive = true
}
variable "rds_postgres_admin_password" {
  type      = string
  sensitive = true
}
# /teams
variable "postgres_teams" { type = set(string) }

# S3
# /postgres
variable "s3_postgres_bucket_arn" { type = string }

# SSM
# /teams
variable "ssm_teams_parameter_paths" { type = map(string) }