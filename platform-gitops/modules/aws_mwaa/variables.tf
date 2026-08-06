variable "kubeconfig_file_path" { type = string }
variable "s3_mwaa_bucket_name"  { type = string }

variable "mwaa_role_arn"                        { type = string }
variable "s3_mwaa_bucket_arn"                   { type = string }
variable "aws_account_id"                       { type = string }
variable "secretsmanager_service_endpoint_url"  { type = string }

variable "teams" {
  type = map(object({
    role_arn = string
  }))
}