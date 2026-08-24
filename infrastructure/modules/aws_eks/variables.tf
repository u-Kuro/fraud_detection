# IAM
# /admin
variable "iam_admin_arn" { type = string }
variable "iam_admin_region" { type = string }
variable "iam_admin_username" {
  type      = string
  sensitive = true
}
variable "iam_admin_password" {
  type      = string
  sensitive = true
}
# /teams
variable "iam_teams_role_arns" { type = map(string) }

# EC2
# /service
variable "ec2_role_arn" { type = string }
variable "ec2_role_name" { type = string }

# EKS
# /service
variable "eks_role_arn" { type = string }
variable "eks_role_name" { type = string }
# /urls
variable "eks_host_endpoint_url" { type = string }
# /teams
variable "eks_teams" { type = set(string) }

# Local Files
# /paths
variable "local_files_kubeconfig_for_localhost_file_path" { type = string }
variable "local_files_kubeconfig_for_docker_file_path" { type = string }
variable "local_files_eks_registries_file_path" { type = string }

# Ministack
# /network
variable "ministack_network_name" { type = string }
variable "ministack_network_gateway" { type = string }

# Secrets Manager
# /teams
variable "secrets_manager_teams_secret_paths" { type = map(string) }

# SSM
# /teams
variable "ssm_teams_parameter_paths" { type = map(string) }