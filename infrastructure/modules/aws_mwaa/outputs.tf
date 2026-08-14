# MWAA
# /urls
output "egress_url" { value = "http://${var.ministack_ip}:${var.ministack_port}" }
# /environment
output "teams_environment_names" { value = { for k, v in aws_mwaa_environment.teams : k => v.name } }
output "teams_environment_connections_prefixes" { value = local.mwaa_teams_airflow_secrets_backend_connections_prefixes }
output "teams_environment_variables_prefixes" { value = local.mwaa_teams_airflow_secrets_backend_variables_prefixes }