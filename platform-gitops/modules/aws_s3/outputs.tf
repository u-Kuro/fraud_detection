output "mlflow_bucket_name" {
  value = aws_s3_bucket.mlflow.bucket
}
output "mlflow_bucket_aws_region" {
  value = aws_s3_bucket.mlflow.region
}

output "mle_bucket_name" {
  value = aws_s3_bucket.mle.bucket
}
output "mle_bucket_aws_region" {
  value = aws_s3_bucket.mle.region
}