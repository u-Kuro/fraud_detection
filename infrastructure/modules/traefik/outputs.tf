# Traefik
# /entrypoints
output "eks_host_entry_point_name" { value = var.traefik_host_entry_point_name }
# /urls
output "eks_host_port" { value = var.eks_container_host_port }