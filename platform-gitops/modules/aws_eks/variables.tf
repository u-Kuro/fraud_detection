variable "aws_account_id" { type = string }

variable "aws_access_key" { type = string }
variable "aws_secret_key" { type = string }
variable "aws_region"     { type = string }

variable "eks_service_endpoint_url" { type = string }

variable "kubeconfig_host_directory_path" { type = string }
variable "kubeconfig_host_file_name"      { type = string }

variable "ecr_registry_endpoint"            { type = string }
variable "ecr_registry_mirror_endpoint_url" { type = string }
variable "ecr_registry_mirror_endpoint"     { type = string }

variable "ecr_registry_secret_name" { type = string }

# From aws_iam module output: map of team_key => IAM Role ARN
variable "team_role_arns" {
  type    = map(string)
  default = {}
}