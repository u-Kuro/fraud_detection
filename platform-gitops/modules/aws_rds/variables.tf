variable "db_username" {
  type      = string
  sensitive = true
}
variable "db_password" {
  type      = string
  sensitive = true
}

variable "rds_role_arn"       { type = string }
variable "s3_rds_bucket_arn"  { type = string }