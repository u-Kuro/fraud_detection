variable "aws_access_key" { type = string }
variable "aws_secret_key" { type = string }
variable "aws_account_id" { type = string }

variable "rds_db_address" { type = string }
variable "rds_db_port"    { type = string }
variable "rds_db_name"    { type = string }

variable "mlflow_db_username" {
  type      = string
  sensitive = true
}
variable "mlflow_db_password" {
  type      = string
  sensitive = true
}

variable "s3_internal_endpoint_url"     { type = string }
variable "s3_mlflow_bucket_aws_region"  { type = string }
variable "s3_mlflow_bucket"             { type = string }
variable "s3_mle_bucket_aws_region"     { type = string }
variable "s3_mle_bucket"                { type = string }