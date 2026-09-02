# MetalLB
# /configurations
output "eks_ip" { value = var.eks_container_ip }
# /resources
output "eks_ip_address_pool_name" { value = var.metallb_eks_ip_address_pool_name }
