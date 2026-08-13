# RDS
resource "aws_db_instance" "postgres" {
  identifier          = "RDS"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = local.rds.postgres.username
  password            = local.rds.postgres.password
  db_name             = "MAIN"
  skip_final_snapshot = true
}
resource "aws_iam_role_policy" "postgres_s3" {
  role = local.rds.role.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "s3:*"
        Resource = [
          local.s3.buckets.postgres.arn,
          "${local.s3.buckets.postgres.arn}/*"
        ]
      }
    ]
  })
}