variable "aws_access_key" { type = string }
variable "aws_secret_key" { type = string }
variable "aws_region"     { type = string }

variable "eks_service_endpoint_url" { type = string }
variable "eks_cluster_name"         { type = string }

variable "s3_service_endpoint_url"  { type = string }
variable "s3_mwaa_bucket"           { type = string }

variable "aws_account_id"  { type = string }

variable "secretsmanager_service_endpoint_url"  { type = string }

# From aws_iam module: map of team_key => IAM Role name
variable "team_role_names" {
  type    = map(string)
  default = {}
}