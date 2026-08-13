output "mlflow_internal_url" {
  value = local.mlflow_url.internal
}
output "mlflow_ingress_url" {
  value = local.mlflow_url.ingress
}

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