# IAM
# /admin
variable "iam_admin_account_id" { type = string }
variable "iam_admin_region" { type = string }
# /teams
variable "iam_teams_names" { type = map(string) }
variable "iam_teams_role_arns" { type = map(string) }
variable "iam_teams_usernames" {
  type      = map(string)
  sensitive = true
}
variable "iam_teams_passwords" {
  type      = map(string)
  sensitive = true
}

# Local Files
# /paths
variable "local_files_kubeconfig_for_docker_file_path" { type = string }
variable "local_files_mwaa_requirements_file_path" { type = string }
# /content
variable "local_files_kubeconfig_for_docker_file_md5" { type = string }
variable "local_files_mwaa_requirements_file_md5" { type = string }
# Ministack
# /container
variable "ministack_network_name" { type = string }
# /urls
variable "ministack_container_ip" { type = string }
variable "ministack_container_port" { type = number }

# MWAA
# /teams
variable "mwaa_teams" { type = set(string) }

# S3
# /mwaa
variable "s3_teams_mwaa_bucket_names" { type = map(string) }
variable "s3_teams_mwaa_bucket_arns" { type = map(string) }
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
variable "secrets_manager_url" { type = string }

# SSM
# /teams
variable "ssm_teams_parameter_paths" { type = map(string) }