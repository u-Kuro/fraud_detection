output "endpoint" {
  description = "Container IP on ministack network — use this as POSTGRES_HOST inside the network"
  value       = aws_db_instance.rds.address
}

output "port" {
  value       = aws_db_instance.rds.port
}