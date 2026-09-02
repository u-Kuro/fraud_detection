# EKS
# /traefik
variable "eks_traefik_namespace" {
  type    = string
  default = "traefik"
}

# MetalLB
# /configurations
variable "metallb_eks_ip" { type = string }
# /resources
variable "metallb_eks_ip_address_pool_name" { type = string }

# Traefik
# /deployment
variable "traefik_host_entry_point_name" {
  type    = string
  default = "eks-host"
}