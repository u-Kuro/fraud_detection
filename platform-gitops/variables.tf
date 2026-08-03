variable "kubeconfig_host_directory_path" {
  type      = string
  default   = "./kubeconfig"
}
variable "kubeconfig_host_file_name" {
  type      = string
  default   = "k3s.yaml"
}

variable "eks_service_endpoint_url" {
  type      = string
  default   = "http://localhost:4566"
}
variable "s3_service_endpoint_url" {
  type      = string
  default   = "http://localhost:4566"
}
variable "secretsmanager_service_endpoint_url" {
  type      = string
  default   = "http://localhost:4566"
}

variable "ecr_registry_endpoint" {
  type      = string
  default   = "localhost:4566"
}
variable "ecr_registry_mirror_endpoint" {
  type      = string
  default   = "ministack:4566"
}
variable "ecr_registry_mirror_endpoint_url" {
  type      = string
  default   = "http://ministack:4566"
}
variable "ecr_registry_secret_name" {
  type      = string
  default   = "ecr_secret"
}
variable "ecr_registry_username" {
  type      = string
  sensitive = true
}
variable "ecr_registry_password" {
  type      = string
  sensitive = true
}

variable "s3_internal_endpoint_url" {
  type      = string
  default   = "http://ministack:4566"
}

variable "aws_access_key" {
  type      = string
  sensitive = true
}
variable "aws_secret_key" {
  type      = string
  sensitive = true
}
variable "aws_region"     { type = string }
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