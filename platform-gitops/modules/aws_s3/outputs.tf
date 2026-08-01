output "mlflow_bucket_name" {
  value = aws_s3_bucket.mlflow.id
}
output "mlflow_bucket_aws_region" {
  value = aws_s3_bucket.mlflow.region
}

output "mwaa_bucket_name" {
  value = aws_s3_bucket.mwaa.id
}
output "mwaa_bucket_aws_region" {
  value = aws_s3_bucket.mwaa.region
}

# NEW
output "team_bucket_names" {
  description = "Map of team name → dedicated S3 bucket name"
  value       = { for k, v in aws_s3_bucket.team : k => v.id }
}