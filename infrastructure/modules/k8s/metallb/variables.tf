# EKS
# /urls
variable "eks_container_ip" {
  type = string
}
# /metallb
variable "eks_metallb_namespace" {
  type    = string
  default = "metallb"
}

# MetalLB
# /resources
variable "metallb_eks_ip_address_pool_name" {
  type    = string
  default = "eks-ip-address-pool"
}
variable "metallb_eks_l2_advertisement_name" {
  type    = string
  default = "eks-l2-advertisement"
}