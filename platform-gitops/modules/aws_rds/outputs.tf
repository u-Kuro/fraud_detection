output "rds" {
  value = {
    identifier  = aws_db_instance.rds.identifier
    address     = aws_db_instance.rds.address
    port        = aws_db_instance.rds.port
    name        = aws_db_instance.rds.db_name
    username    = aws_db_instance.rds.username
    password    = aws_db_instance.rds.password
  }
  sensitive = true
}