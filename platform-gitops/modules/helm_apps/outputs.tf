output "mlflow_tracking_uri"  {
  value = local.mlflow_tracking_uri
}
output "mlflow_release"  {
  value = helm_release.mlflow.status
}