resource "aws_db_instance" "rds" {
  identifier          = "rds"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = var.db_username
  password            = var.db_password
  db_name             = "main"
  skip_final_snapshot = true
}

resource "aws_iam_role_policy" "rds" {
  role = var.rds_role_arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject*",
          "s3:GetObject*",
          "s3:ListBucket",
          "s3:DeleteObject*",
          "s3:GetBucketLocation"
        ]
        Resource = [
          var.s3_rds_bucket_arn,
          "${var.s3_rds_bucket_arn}/*"
        ]
      }
    ]
  })
}