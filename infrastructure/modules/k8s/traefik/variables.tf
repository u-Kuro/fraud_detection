# EKS
# /urls
variable "eks_container_ip" {
  type = string
}
variable "eks_container_host_port" {
  type = number
}
# /traefik
variable "eks_traefik_namespace" {
  type    = string
  default = "traefik"
}

# Traefik
# /deployment
variable "traefik_web_node_port" {
  type    = number
  default = 30000
}
variable "traefik_host_entry_point_name" {
  type    = string
  default = "eks-host"
}