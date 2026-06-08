variable "aws_access_key" {
  type        = string
}

variable "aws_secret_key" {
  type        = string
  sensitive   = true
}

variable "aws_region" {
  type        = string
  description = "The target AWS region where all infrastructure components will be provisioned."
}

variable "aws_account_id" {
  type        = string
}

variable "eks_cluster_name" {
  type        = string
  description = "The unique identifier name for the managed EKS/Kubernetes cluster."
}

variable "rds_db_name" {
  type        = string
  description = "The database name to be automatically created inside the RDS database instance."
}

variable "rds_db_username" {
  type        = string
  description = "The administrative username used to authenticate against the RDS database instance."
}

variable "rds_db_password" {
  type        = string
  sensitive   = true
  description = "The administrative password for the RDS database instance."
}

variable "s3_dags_bucket" {
  type        = string
  description = "The name of the S3 bucket designated to store and sync Apache Airflow DAG code files."
}

variable "s3_mlflow_artifacts_bucket" {
  type        = string
  description = "The name of the S3 bucket designated to store and track MLflow artifacts."
}

variable "ecr_repository_name" {
  type        = string
  description = "The name of the ECR repository used to hold built container images."
}

variable "slack_bot_token" {
  type        = string
  sensitive   = true
  description = "The OAuth bot user token (xoxb-...) used by the application to send notifications to Slack channels."
}

variable "slack_app_token" {
  type        = string
  sensitive   = true
  description = "The WebSocket App-Level Token (xapp-...) required to manage connections via Slack's Socket Mode API."
}
