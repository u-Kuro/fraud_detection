# MiniStack
# /configurations
output "name" { value = docker_container.ministack.name }
output "port" { value = local.ministack_container_port }
output "host_port" { value = local.ministack_container_host_port }
output "ip" { value = tolist(local.ministack_container_networks)[0].ip_address }
# /urls
output "endpoint" { value = "${docker_container.ministack.name}:${local.ministack_container_port}" }
output "url" { value = "http://${docker_container.ministack.name}:${local.ministack_container_port}" }
output "host_url" { value = "http://localhost:${local.ministack_container_host_port}" }