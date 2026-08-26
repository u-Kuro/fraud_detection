# Create MetalLB release
resource "helm_release" "metallb" {
  name             = "metallb"
  repository       = "https://metallb.github.io/metallb"
  chart            = "metallb"
  version          = "0.16.1" # v0.16.1 https://artifacthub.io/packages/helm/metallb/metallb/0.16.1
  namespace        = var.eks_metallb_namespace
  create_namespace = true
  wait             = true
  wait_for_jobs    = true
  timeout          = 600
}
# Create pool with K3s IP for Traefik
resource "kubectl_manifest" "eks_ip_address_pool" {
  yaml_body = yamlencode({
    apiVersion = "metallb.io/v1beta1"
    kind       = "IPAddressPool"
    metadata = {
      name      = var.metallb_eks_ip_address_pool_name
      namespace = var.eks_metallb_namespace
    }
    spec = {
      addresses = ["${var.eks_container_ip}/32"]
    }
  })
  depends_on = [
    helm_release.metallb
  ]
}
# Create L2 advertisement to satisfy requirement to activate the address pool
resource "kubectl_manifest" "eks_l2_advertisement" {
  yaml_body = yamlencode({
    apiVersion = "metallb.io/v1beta1"
    kind       = "L2Advertisement"
    metadata = {
      name      = var.metallb_eks_l2_advertisement_name
      namespace = var.eks_metallb_namespace
    }
    spec = {
      ipAddressPools = [var.metallb_eks_ip_address_pool_name]
    }
  })
  depends_on = [
    kubectl_manifest.eks_ip_address_pool
  ]
}