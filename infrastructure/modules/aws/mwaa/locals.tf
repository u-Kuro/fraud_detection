locals {
  # MWAA
  # /environment-configurations
  mwaa_secrets_backend_aws_profile_name       = "default"
  mwaa_airflow_version                        = "3.3.1-python3.12" # v3.12.13 | core.executor: LocalExecutor
  mwaa_airflow_python_packages_constraint_url = "https://raw.githubusercontent.com/apache/airflow/constraints-3.3.1/constraints-3.12.txt"
  # /urls
  mwaa_urls = { for k, v in aws_mwaa_environment.teams : k => "http://${v.webserver_url}" } # 172.19.0.5:[8080|internal-port]
  # /teams
  mwaa_teams_environment_names                            = { for v in var.mwaa_teams : v => v }
  mwaa_teams_environment_dag_s3_paths                     = { for v in var.mwaa_teams : v => "${var.s3_teams_mwaa_dag_path}/" }
  mwaa_teams_airflow_secrets_backend_connections_prefixes = { for v in var.mwaa_teams : v => "airflow/connections/${v}" }
  mwaa_teams_airflow_secrets_backend_variables_prefixes   = { for v in var.mwaa_teams : v => "airflow/variables/${v}" }

  # Secrets Manager
  # /arns
  secrets_manager_base_arn = "arn:aws:secretsmanager:*:${var.iam_admin_account_id}:secret"
  # /teams
  secrets_manager_mwaa_teams_airflow_secrets_backend_connections_arns = {
    for k, v in local.mwaa_teams_airflow_secrets_backend_connections_prefixes : k => "${local.secrets_manager_base_arn}:${v}"
  }
  secrets_manager_mwaa_teams_airflow_secrets_backend_variables_arns = {
    for k, v in local.mwaa_teams_airflow_secrets_backend_variables_prefixes : k => "${local.secrets_manager_base_arn}:${v}"
  }
}
# Initialize Apache Airflow's default configurations
resource "local_sensitive_file" "mwaa_teams_aws_config" {
  for_each        = aws_mwaa_environment.teams
  filename        = "${var.local_files_directory_path}/aws/${each.key}/config"
  file_permission = "0600"
  content         = <<-EOF
    [default]
    region = ${var.iam_admin_region}
    endpoint_url = ${var.secrets_manager_url}
    request_checksum_calculation = when_required
  EOF
}
# Initialize Apache Airflow's default credentials
resource "local_sensitive_file" "mwaa_teams_aws_credentials" {
  for_each        = aws_mwaa_environment.teams
  filename        = "${var.local_files_directory_path}/aws/${each.key}/credentials"
  file_permission = "0600"
  content         = <<-EOF
    [default]
    aws_access_key_id = ${var.iam_teams_usernames[each.key]}
    aws_secret_access_key = ${var.iam_teams_passwords[each.key]}
  EOF
}