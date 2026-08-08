output "name" {
  value = aws_mwaa_environment.mwaa.name
}
output "webserver_url" {
  value = aws_mwaa_environment.mwaa.webserver_url
}

output "kubeconfig_mwaa_file_path" {
  value = local.mwaa_kubeconfig_file_path
}