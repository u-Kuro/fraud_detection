output "rds_bucket" {
  value = {
    name   = aws_s3_bucket.rds.id
    arn    = aws_s3_bucket.rds.arn
    region = aws_s3_bucket.rds.region
  }
}

output "mlflow_bucket" {
  value = {
    name   = aws_s3_bucket.mlflow.id
    arn    = aws_s3_bucket.mlflow.arn
    region = aws_s3_bucket.mlflow.region
  }
}

output "teams_buckets" {
  value = {
    for k, v in aws_s3_bucket.teams : k => {
      name   = v.id
      arn    = v.arn
      region = v.region
    }
  }
}

output "teams_mwaa_buckets" {
  value = {
    for k, v in aws_s3_bucket.teams_mwaa : k => {
      name   = v.id
      arn    = v.arn
      region = v.region
    }
  }
}