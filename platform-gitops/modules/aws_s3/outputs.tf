output "mwaa_bucket" {
  value = {
    name   = aws_s3_bucket.mwaa.id
    arn    = aws_s3_bucket.mwaa.arn
    region = aws_s3_bucket.mwaa.region
  }
}

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

output "mwaa_teams_buckets" {
  value = {
    for k, v in aws_s3_bucket.mwaa_teams : k => {
      name   = v.id
      arn    = v.arn
      region = v.region
    }
  }
}