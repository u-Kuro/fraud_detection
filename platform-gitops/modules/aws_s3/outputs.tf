output "mwaa_bucket_name" {
  value = aws_s3_bucket.mwaa.id
}
output "mwaa_bucket_arn" {
  value = aws_s3_bucket.mwaa.arn
}
output "mwaa_bucket_aws_region" {
  value = aws_s3_bucket.mwaa.region
}

output "rds_bucket_name" {
  value = aws_s3_bucket.rds.id
}
output "rds_bucket_arn" {
  value = aws_s3_bucket.rds.arn
}
output "rds_bucket_aws_region" {
  value = aws_s3_bucket.rds.region
}

output "mlflow_bucket_name" {
  value = aws_s3_bucket.mlflow.id
}
output "mlflow_bucket_arn" {
  value = aws_s3_bucket.mlflow.arn
}
output "mlflow_bucket_aws_region" {
  value = aws_s3_bucket.mlflow.region
}