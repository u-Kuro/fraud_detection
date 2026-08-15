# MLflow
# /urls
output "mlflow_inter_url" {
  value = "http://${var.mlflow_host}.${var.eks_mlflow_namespace}.svc.cluster.local:${var.eks_traefik_http_port}"
}
output "mlflow_intra_url" {
  value = local.mlflow_intra_url
}
# /teams
output "mlflow_teams_workspace_names" { value = {for v in local.mlflow.users.teams : v =>  }
output "mlflow_team_workspaces" {
  value = {
    for v in local.mlflow.users.teams : v => {
      namespace = v
      username  = v
      password  = v # team can change it themselves (PATCH /api/2.0/mlflow/users/update-password)
    }
  }
  sensitive = true
}