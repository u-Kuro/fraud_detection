# Docker Network
# /configurations
variable "main_docker_network_name" { type = string }

# MiniStack
# /configurations
variable "ministack_container_port" {
  type    = number
  default = 4566
}
variable "ministack_container_host_port" {
  type    = number
  default = 4566
}