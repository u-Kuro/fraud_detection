# MLflow
# /urls
output "inter_url" {
  value = "http://${var.mlflow_host}.${var.eks_mlflow_namespace}.svc.cluster.local:${var.eks_traefik_http_port}"
}
output "intra_url" {
  value = local.mlflow_intra_url
}
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