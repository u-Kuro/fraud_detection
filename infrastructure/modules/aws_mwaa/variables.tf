# IAM
# /admin
variable "iam_admin_account_id" { type = string }
# /teams
variable "iam_teams_names" { type = map(string) }
variable "iam_teams_role_arns" { type = map(string) }

# Local Files
# /paths
variable "local_files_mwaa_requirements_file_path" { type = string }
variable "local_files_kubeconfig_container_file_path" { type = string }

# Ministack
variable "ministack_ip" { type = string }
variable "ministack_port" { type = number }

# MWAA
# /teams
variable "mwaa_teams" { type = set(string) }

# S3
# /mwaa
variable "s3_teams_mwaa_bucket_name" { type = string }
variable "s3_teams_mwaa_bucket_arn" { type = string }
variable "s3_teams_mwaa_requirements_file_path" {
  type    = string
  default = "requirements.txt"
}
variable "s3_teams_mwaa_dag_path" {
  type    = string
  default = "dag"
}
variable "s3_teams_mwaa_kubeconfig_file_path" {
  type    = string
  default = "kubeconfig.yaml" # /usr/local/airflow/dags/[s3_kubeconfig_file_path_for_mwaa]
}

# Secrets Manager
# /urls
variable "secrets_manager_container_endpoint_url" { type = string }

# SSM Parameter
# /teams
variable "ssm_teams_parameter_path" { type = map(string) }