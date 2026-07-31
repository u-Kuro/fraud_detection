resource "aws_db_instance" "main" {
  identifier          = "rds"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = var.db_username
  password            = var.db_password
  db_name             = "main"
  skip_final_snapshot = true
}