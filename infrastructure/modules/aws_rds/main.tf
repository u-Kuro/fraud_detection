# Create Postgres in RDS
resource "aws_db_instance" "postgres" {
  identifier          = "rds"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = var.rds_postgres_admin_username
  password            = var.rds_postgres_admin_password
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
# Get Ministack's Postgres container configurations
data "external" "postgres_configuration" {
  depends_on = [aws_db_instance.postgres]

  program = ["powershell", "-File", "${path.module}/scripts/get-postgres-configurations.ps1"]

  query = {
    ministack_network_name = var.ministack_network_name
    postgres_endpoint_ip   = aws_db_instance.postgres.address
  }
}