output "identifier" {
  value = aws_db_instance.main.identifier
}
output "address" {
  value = aws_db_instance.main.address
}
output "port" {
  value = aws_db_instance.main.port
}
output "name" {
  value = aws_db_instance.main.db_name
}

output "username" {
  value = aws_db_instance.main.username
}
output "password" {
  value = aws_db_instance.main.password
  sensitive = true
}
