output "buckets" {
  value = {
    postgres = {
      name   = aws_s3_bucket.postgres.id
      arn    = aws_s3_bucket.postgres.arn
      region = aws_s3_bucket.postgres.region
    }
    mlflow = {
      name   = aws_s3_bucket.mlflow.id
      arn    = aws_s3_bucket.mlflow.arn
      region = aws_s3_bucket.mlflow.region
    }
    teams = {
      for k, v in aws_s3_bucket.teams : k => {
        name   = v.id
        arn    = v.arn
        region = v.region
      }
    }
    teams_mwaa = {
      for k, v in aws_s3_bucket.teams_mwaa : k => {
        name   = v.id
        arn    = v.arn
        region = v.region
      }
    }
  }
}