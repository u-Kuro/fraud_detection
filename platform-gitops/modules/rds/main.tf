resource "aws_db_instance" "rds" {
  identifier          = var.db_name
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  username            = var.db_username
  password            = var.db_password
  db_name             = var.db_name
  skip_final_snapshot = true
  apply_immediately   = true
}