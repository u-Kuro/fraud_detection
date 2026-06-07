output "rds_endpoint" {
  description = "RDS container IP on ministack_network (routable from k3s pods and Airflow)"
  value       = module.rds.endpoint
}

output "ecr_registry" {
  value = module.ecr.repository_url
}

output "mwaa_webserver_url" {
  value = module.mwaa.webserver_url
}

output "kubeconfig_path" {
  description = "Host-patched kubeconfig for kubectl from Windows host"
  value       = "${path.root}/kubeconfig/k3s.yaml"
}