output "dags_bucket_name" {
  value = aws_s3_bucket.dags.bucket
}
output "dags_bucket_aws_region" {
  value = aws_s3_bucket.dags.region
}

output "mlflow_bucket_name" {
  value = aws_s3_bucket.mlflow.bucket
}
output "mlflow_bucket_aws_region" {
  value = aws_s3_bucket.mlflow.region
}
