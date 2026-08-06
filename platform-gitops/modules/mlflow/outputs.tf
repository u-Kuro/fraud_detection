output "mlflow_tracking_uri" {
  value = local.mlflow_tracking_uri
}

output "mlflow_team_workspaces" {
  value = {
    for k, v in random_password.teams : k => {
      namespace = k
      username = k
      password = v.result
    }
  }
  sensitive = true
}