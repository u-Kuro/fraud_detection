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
}
variable "rds_postgres_admin_password" {
  type      = string
  sensitive = true
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

locals {
  ministack_container_name               = "ministack"
  local_files_directory_path             = "${path.root}/local_files"
  scripts_directory_path                 = "${path.root}/scripts"
  secrets_manager_container_endpoint_url = "http://${local.ministack_container_name}:4566"
}
data "external" "ministack_configuration" {
  program     = ["powershell", "-File", "${local.scripts_directory_path}/get-ministack-configuration.ps1"]
  working_dir = path.root
}
locals {
  ministack_container_name      = data.external.ministack_configuration.result.ministack_container_name
  ministack_network_name        = data.external.ministack_configuration.result.ministack_network_name
  ministack_network_gateway     = data.external.ministack_configuration.result.ministack_network_gateway
  ministack_container_ip        = data.external.ministack_configuration.result.ministack_container_ip
  ministack_container_host_port = data.external.ministack_configuration.result.ministack_container_host_port
}
locals {
  s3_egress_url = "http://${local.ministack_container_ip}:4566"
}
variable "eks_host_endpoint_url" {
  type    = string
  default = "http://localhost:4566"
}
variable "s3_host_endpoint_url" {
  type    = string
  default = "http://localhost:4566"
}
variable "secrets_manager_host_endpoint_url" {
  type    = string
  default = "http://localhost:4566"
}
data "aws_ecr_authorization_token" "token" {}
locals {
  ecr_aws_endpoint        = replace(data.aws_ecr_authorization_token.token.proxy_endpoint, "/^[^:]+:\\/\\//", "")
  ecr_username            = data.aws_ecr_authorization_token.token.user_name
  ecr_password            = data.aws_ecr_authorization_token.token.password
  ecr_authorization_token = data.aws_ecr_authorization_token.token.authorization_token
}
variable "ecr_container_endpoint" {
  type    = string
  default = "ministack:4566"
}
variable "ecr_container_endpoint_url" {
  type    = string
  default = "http://ministack:4566"
}
