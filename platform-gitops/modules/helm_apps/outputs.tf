output "mlflow_tracking_uri"  {
  value = "http://${var.mlflow_host}:${var.mlflow_port}"
}