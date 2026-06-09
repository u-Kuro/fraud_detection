variable "s3_internal_endpoint_url" {
  type = string
}

variable "aws_access_key" {
  type = string
}
variable "aws_secret_key" {
  type = string
}
variable "aws_region" {
  type = string
}

variable "rds_db_address" {
  type = string
}
variable "rds_db_port" {
  type = string
}
variable "rds_db_name" {
  type = string
}
variable "rds_db_username" {
  type = string
}
variable "rds_db_password" {
  type      = string
  sensitive = true
}

variable "s3_mlflow_bucket_name" {
  type = string
}

variable "slack_bot_token" {
  type      = string
  sensitive = true
}
variable "slack_app_token" {
  type      = string
  sensitive = true
}
