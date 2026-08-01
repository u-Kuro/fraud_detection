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

variable "teams" {
  description = "Team definitions used for EKS Access Entries"
  type = map(object({
    namespace = string
  }))
}

variable "team_role_arns" {
  description = "Map of team name → IRSA role ARN (from aws_iam_oidc module)"
  type        = map(string)
}