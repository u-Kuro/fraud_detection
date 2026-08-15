# Create Postgres in RDS
resource "aws_db_instance" "postgres" {
  identifier          = "rds"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = var.rds_postgres_username
  password            = var.rds_postgres_password
  db_name             = "main"
  skip_final_snapshot = true
}
# Allow snapshots/backup in RDS
resource "aws_iam_role_policy" "rds" {
  role = var.rds_role_name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "s3:*"
        Resource = [
          var.s3_postgres_bucket_arn,
          "${var.s3_postgres_bucket_arn}/*"
        ]
      }
    ]
  })
}