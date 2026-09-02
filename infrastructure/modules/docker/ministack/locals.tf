locals {
  # MiniStack
  # /configurations
  ministack_container_networks = [
    for network in docker_container.ministack.network_data : network
    if network.network_name == var.main_docker_network_name
  ]
  ministack_container_ports     = docker_container.ministack.ports
  ministack_container_port      = tonumber(tolist(local.ministack_container_ports)[0].internal)
  ministack_container_host_port = tonumber(tolist(local.ministack_container_ports)[0].external)
}