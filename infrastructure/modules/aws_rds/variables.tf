# RDS
# /service
variable "rds_role_name" {type = string}
# /postgres
variable "rds_postgres_username" {
  type = string
  sensitive = true
}
variable "rds_postgres_password" {
  type = string
  sensitive = true
}

# S3
# /postgres
variable "s3_postgres_bucket_arn" {type = string}