# RDS
resource "aws_db_instance" "rds" {
  identifier          = "rds"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = var.rds.username
  password            = var.rds.password
  db_name             = "main"
  skip_final_snapshot = true
}
resource "aws_iam_role_policy" "rds" {
  role = var.rds.role.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "s3:*"
        Resource = [
          var.s3.buckets.rds.arn,
          "${var.s3.buckets.rds.arn}/*"
        ]
      }
    ]
  })
}