output "mlflow_internal_url" {
  value = local.mlflow_url.internal
}
output "mlflow_external_url" {
  value = local.mlflow_url.external
}

output "mlflow_team_workspaces" {
  value = {
    for v in local.aws.users.mlflow_teams : v => {
      namespace = v
      username  = v
      password  = v # team can change it themselves (PATCH /api/2.0/mlflow/users/update-password)
    }
  }
  sensitive = true
}