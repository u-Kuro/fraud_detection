locals {
  local_files_directory_path = "${path.root}/local_files"
  scripts_directory_path     = "${path.root}/scripts"
}
data "external" "ministack_ip" {
  program     = ["powershell", "-File", "${local.scripts_directory_path}/get_ministack_network_ip.ps1"]
  working_dir = path.root
  query = {
    ministack_network_name = "ministack_network"
    ministack_container_name = "ministack"
  }
}
locals {
  ministack_ip = data.external.ministack_ip.result.ip
}
locals {
  s3_network_endpoint_url = "${local.ministack_ip}:4566"
}
variable "eks_host_endpoint_url" {
  type    = string
  default = "http://localhost:4566"
}
variable "s3_host_endpoint_url" {
  type    = string
  default = "http://localhost:4566"
}
variable "secretsmanager_host_endpoint_url" {
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
variable "ecr_secret_name" {
  type    = string
  default = "ecr_secret"
}
variable "ecr_username" {
  type      = string
  sensitive = true
}
variable "ecr_password" {
  type      = string
  sensitive = true
}

variable "aws_access_key" {
  type      = string
  sensitive = true
}
variable "aws_secret_key" {
  type      = string
  sensitive = true
}
variable "aws_region" { type = string }
variable "aws_account_id" { type = string }

variable "rds_db_username" {
  type      = string
  sensitive = true
}
variable "rds_db_password" {
  type      = string
  sensitive = true
}

variable "mlflow_postgresql_username" {
  type      = string
  sensitive = true
}
variable "mlflow_postgresql_password" {
  type      = string
  sensitive = true
}
variable "mlflow_flask_server_secret_key" {
  type      = string
  sensitive = true
}
variable "mle_postgresql_username" {
  type      = string
  sensitive = true
}
variable "mle_postgresql_password" {
  type      = string
  sensitive = true
}
variable "mle_migrations_postgresql_username" {
  type      = string
  sensitive = true
}
variable "mle_migrations_postgresql_password" {
  type      = string
  sensitive = true
}