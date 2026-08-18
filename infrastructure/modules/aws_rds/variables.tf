# # Ministack
# # /network
variable "ministack_network_name" { type = string }
variable "ministack_network_gateway" { type = string }

# RDS
# /service
variable "rds_role_name" { type = string }
# /postgres
variable "rds_postgres_admin_username" {
  type      = string
  sensitive = true
}
variable "rds_postgres_admin_password" {
  type      = string
  sensitive = true
}

# S3
# /postgres
variable "s3_postgres_bucket_arn" { type = string }