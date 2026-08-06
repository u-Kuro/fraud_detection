output "rds" {
  value = {
    identifier = aws_db_instance.rds.identifier
    host       = aws_db_instance.rds.address
    port       = tonumber(aws_db_instance.rds.port)
    db_name    = aws_db_instance.rds.db_name
    username   = aws_db_instance.rds.username
    password   = aws_db_instance.rds.password
  }
  sensitive = true
}