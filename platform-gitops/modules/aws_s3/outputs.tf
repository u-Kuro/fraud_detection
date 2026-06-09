output "dags_bucket_name" {
  value = aws_s3_bucket.dags.bucket_name
}

output "mlflow_bucket_name" {
  value = aws_s3_bucket.mlflow.bucket_name
}
