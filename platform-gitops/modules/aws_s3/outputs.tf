output "mlflow_bucket_name" {
  value = aws_s3_bucket.mlflow.id
}
output "mlflow_bucket_aws_region" {
  value = aws_s3_bucket.mlflow.region
}

output "mle_bucket_name" {
  value = aws_s3_bucket.mle.id
}
output "mle_bucket_aws_region" {
  value = aws_s3_bucket.mle.region
}