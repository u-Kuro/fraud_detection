variable "kubeconfig_host_directory_path" {
  type      = string
  default   = "./kubeconfig"
}
variable "k3s_mount_file_name" {
  type      = string
  default   = "k3s.yaml"
}

variable "eks_service_endpoint_url" {
  type      = string
  default   = "http://localhost:4566"
}#
variable "s3_service_endpoint_url" {
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
  default   = "ecr-secret"
}

variable "s3_internal_endpoint_url" {
  type      = string
  default   = "http://ministack:4566"
}

# service endpoint url for eks s3
# registry endpoint url for ecr (mini
#
variable "aws_access_key" {
  type      = string
  sensitive = true
}
variable "aws_secret_key" {
  type      = string
  sensitive = true
}
variable "aws_region" {
  type      = string
}
variable "aws_account_id" {
  type      = string
}

variable "ecr_repository_name" {
  type      = string
  default   = "fraud_detection_ecr"
}

variable "eks_cluster_name" {
  type      = string
  default   = "fraud_detection_eks"
}

variable "mwaa_environment_name" {
  type      = string
  default   = "fraud_detection_mwaa"
}

variable "rds_db_identifier" {
  type      = string
  default   = "fraud-detection-rds"
}
variable "rds_db_username" {
  type      = string
  sensitive = true
}
variable "rds_db_password" {
  type      = string
  sensitive = true
}

variable "s3_dags_bucket_name" {
  type      = string
  default   = "dags"
}
variable "s3_mlflow_bucket_name" {
  type      = string
  default   = "mlflow"
}

variable "slack_bot_token" {
  type      = string
  sensitive = true
}
variable "slack_app_token" {
  type      = string
  sensitive = true
}
