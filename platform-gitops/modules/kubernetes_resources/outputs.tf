output "team_namespaces" {
  description = "Map of team name → Kubernetes namespace name"
  value       = { for k, v in kubernetes_namespace.team : k => v.metadata[0].name }
}

output "team_service_accounts" {
  description = "Map of team name → service account name"
  value       = { for k, v in kubernetes_service_account.team : k => v.metadata[0].name }
}

output "shared_configmap_name" {
  description = "Name of the shared platform ConfigMap"
  value       = kubernetes_config_map.shared.metadata[0].name
}
