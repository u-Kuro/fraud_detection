# IAM
# /admin
variable "iam_admin_arn" { type = string }
# /teams
variable "iam_teams_arns" { type = map(string) }
# /services
variable "iam_ec2_role_arn" { type = string }
variable "iam_ec2_role_name" { type = string }
variable "iam_eks_role_arn" { type = string }
variable "iam_eks_role_name" { type = string }

# EKS
# /teams
variable "eks_teams" { type = set(string) }
variable "eks_teams_namespaces" { type = map(string) }

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