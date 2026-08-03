variable "aws_access_key" {
  type      = string
  sensitive = true
}
variable "aws_secret_key" {
  type      = string
  sensitive = true
}
variable "aws_region"     { type = string }

variable "eks_service_endpoint_url" { type = string }
variable "eks_cluster_name"         { type = string }

variable "s3_service_endpoint_url"  { type = string }
variable "s3_mwaa_bucket_name"      { type = string }
variable "s3_mwaa_bucket_arn"       { type = string }

variable "aws_account_id"  { type = string }

variable "secretsmanager_service_endpoint_url"  { type = string }

variable "teams" {
  type = map(object({
    name = string
  }))
}