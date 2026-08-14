# S3
# /postgres
output "postgres_bucket_name" { value = aws_s3_bucket.postgres.id}
output "postgres_bucket_arn" {value = aws_s3_bucket.postgres.arn}
output "postgres_bucket_region" {value = aws_s3_bucket.postgres.region}
# /mlflow
output "mlflow_bucket_name" { value = aws_s3_bucket.mlflow.id}
output "mlflow_bucket_arn" {value = aws_s3_bucket.mlflow.arn}
output "mlflow_bucket_region" {value = aws_s3_bucket.mlflow.region}
# /teams
output "teams_bucket_names" { value = { for k, v in aws_s3_bucket.teams : k => v.id }}
output "teams_bucket_arns" {value = { for k, v in aws_s3_bucket.teams : k => v.arn }}
output "teams_bucket_regions" {value = { for k, v in aws_s3_bucket.teams : k => v.region }}
# /teams-mwaa
output "teams_mwaa_bucket_names" { value = { for k, v in aws_s3_bucket.teams_mwaa : k => v.id }}
output "teams_mwaa_bucket_arns" {value = { for k, v in aws_s3_bucket.teams_mwaa : k => v.arn }}
output "teams_mwaa_bucket_regions" {value = { for k, v in aws_s3_bucket.teams_mwaa : k => v.region }}