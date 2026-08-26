# MWAA
# /urls
output "egress_url" { value = "http://${var.ministack_container_ip}:${var.ministack_container_port}" }
# /teams
output "teams_host_url" { value = { for k, v in data.external.airflow_configuration : k => "http://localhost:${v.result.airflow_container_host_port}" } }
# /environment
output "teams_environment_names" { value = { for k, v in aws_mwaa_environment.teams : k => v.name } }
output "teams_environment_connections_prefixes" { value = local.mwaa_teams_airflow_secrets_backend_connections_prefixes }
output "teams_environment_variables_prefixes" { value = local.mwaa_teams_airflow_secrets_backend_variables_prefixes }
output "teams_environment_kubeconfig_file_paths" { value = { for k, v in data.external.airflow_configuration : k => v.result.airflow_container_kubeconfig_file_path } }