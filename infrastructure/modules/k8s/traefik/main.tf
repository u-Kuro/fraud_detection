resource "helm_release" "traefik" {
  name             = "traefik"
  repository       = "https://traefik.github.io/charts"
  chart            = "traefik"
  version          = "41.2.0" # v3.7.10 https://artifacthub.io/packages/helm/traefik/traefik/41.2.0
  namespace        = var.eks_traefik_namespace
  create_namespace = true
  wait             = true
  wait_for_jobs    = true

  values = [file("${path.module}/configurations/values.yaml")]

  set = [
    { name = "service.spec.loadBalancerIP", value = var.metallb_eks_ip },
    { name = "service.annotations.metallb\\.io/address-pool", value = var.metallb_eks_ip_address_pool_name },
    { name = "ports.${var.traefik_host_entry_point_name}.port", value = var.eks_container_host_port },
  ]
}