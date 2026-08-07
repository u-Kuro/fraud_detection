output "mlflow_tracking_uri" {
  value = local.mlflow_tracking_uri
}

output "mlflow_team_workspaces" {
  value = {
    for v in var.mlflow_teams : v => {
      namespace = v
      username = v
      password = v # team can change it themselves (PATCH /api/2.0/mlflow/users/update-password)
    }
  }
  sensitive = true
}