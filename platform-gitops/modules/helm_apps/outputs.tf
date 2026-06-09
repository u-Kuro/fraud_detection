output "mlflow_release"  {
  value = helm_release.mlflow.status
}

output "fastapi_release" {
  value = helm_release.fastapi.status
}
