output "postgres" {
  value = {
    identifier = aws_db_instance.postgres.identifier
    host       = aws_db_instance.postgres.address
    port       = tonumber(aws_db_instance.postgres.port)
    db_name    = aws_db_instance.postgres.db_name
    username   = aws_db_instance.postgres.username
    password   = aws_db_instance.postgres.password
  }
  sensitive = true
}