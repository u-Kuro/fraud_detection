output "identifier" {
  value = aws_db_instance.rds.identifier
}
output "address" {
  value = aws_db_instance.rds.address
}
output "port" {
  value = aws_db_instance.rds.port
}
output "name" {
  value = aws_db_instance.rds.db_name
}

output "username" {
  value     = aws_db_instance.rds.username
  sensitive = true
}
output "password" {
  value     = aws_db_instance.rds.password
  sensitive = true
}
