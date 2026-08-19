locals {
  # MWAA
  # /urls
  mwaa_urls = { for k, v in aws_mwaa_environment.teams : k => "http://${v.webserver_url}" } # 172.19.0.5:[8080|internal-port]
  # /teams
  mwaa_teams_environment_names        = { for v in var.mwaa_teams : v => v }
  mwaa_teams_environment_dag_s3_paths = { for k in var.mwaa_teams : k => "${var.s3_teams_mwaa_dag_path}/" }
  mwaa_teams_airflow_secrets_backend_connections_prefixes = { for v in var.mwaa_teams : k => "airflow/connections/${v}" }
  mwaa_teams_airflow_secrets_backend_variables_prefixes   = { for v in var.mwaa_teams : k => "airflow/variables/${v}" }

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