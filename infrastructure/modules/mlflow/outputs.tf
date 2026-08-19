# MLflow
# /urls
output "inter_url" { value = local.mlflow_inter_url }
output "intra_url" { value = local.mlflow_intra_url }
output "ingress_url" { value = local.mlflow_ingress_url }
# /teams
output "teams_workspace_names" { value = local.mlflow_teams_workspace_names }
output "teams_usernames" {
  value     = local.mlflow_teams_usernames
  sensitive = true
}
output "teams_passwords" {
  value     = local.mlflow_teams_passwords
  sensitive = true
}