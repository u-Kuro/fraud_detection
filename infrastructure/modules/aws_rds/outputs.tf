# RDS
# /postgres
output "postgres_identifier" { value = aws_db_instance.postgres.identifier }
output "postgres_host" { value = aws_db_instance.postgres.address }
output "postgres_port" { value = tonumber(aws_db_instance.postgres.port) }
# output "postgres_egress_host" { value = var.ministack_network_gateway }
# output "postgres_egress_port" { value = tonumber(data.external.postgres_configuration.result.postgres_container_host_port) }
output "postgres_db_name" { value = aws_db_instance.postgres.db_name }
output "postgres_username" {
  value     = aws_db_instance.postgres.username
  sensitive = true
}
output "postgres_password" {
  value     = aws_db_instance.postgres.password
  sensitive = true
}
