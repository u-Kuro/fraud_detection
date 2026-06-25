variable "environment_name" {
  type    = string
  default = "mle_mwaa"
}

variable "aws_access_key"  { type = string }
variable "aws_secret_key"  { type = string }
variable "aws_region"      { type = string }
variable "aws_account_id"  { type = string }

variable "eks_service_endpoint_url" { type = string }
variable "s3_service_endpoint_url"  { type = string }

variable "eks_cluster_name" { type = string }
variable "s3_mle_bucket"    { type = string }