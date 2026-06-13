output "name" {
  value = aws_mwaa_environment.main.name
}
output "webserver_url" {
  value = aws_mwaa_environment.main.webserver_url
}
output "dags_s3_path" {
  value = aws_mwaa_environment.main.dag_s3_path
}
