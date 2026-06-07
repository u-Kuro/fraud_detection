output "s3_dags_bucket_name" {
  value = aws_s3_bucket.dags.bucket_name
}

output "s3_mlflow_bucket_name" {
  value = aws_s3_bucket.mlflow_artifacts.bucket_name
}