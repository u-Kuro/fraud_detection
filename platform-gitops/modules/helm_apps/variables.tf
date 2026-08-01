variable "mlflow_host" {
  type = string
  default = "mlflow"
}
variable "mlflow_port" {
  type = string
  default = 5000
}

variable "rds_db_address" { type = string }
variable "rds_db_port"    { type = string }
variable "rds_db_name"    { type = string }

variable "s3_internal_endpoint_url"     { type = string }
variable "s3_mlflow_bucket_aws_region"  { type = string }
variable "s3_mlflow_bucket"             { type = string }

variable "mlflow_db_username" {
  type      = string
  sensitive = true
}
variable "mlflow_db_password" {
  type      = string
  sensitive = true
}

variable "aws_access_key" {
  type = string
  sensitive = true
}
variable "aws_secret_key" {
  type = string
  sensitive = true
}



variable "teams" {
  description = "Team definitions — only mlflow_workspace is used here"
  type = map(object({
    mlflow_workspace = optional(string)
  }))
  default = {}
}