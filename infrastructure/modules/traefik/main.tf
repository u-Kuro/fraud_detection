resource "helm_release" "traefik" {
  name             = "traefik"
  repository       = "https://helm.traefik.io/traefik"
  chart            = "traefik"
  version          = "41.2.0" # v3.7.10 https://artifacthub.io/packages/helm/traefik/traefik/41.2.0
  namespace        = var.eks_traefik_namespace
  create_namespace = true
  wait             = true
  wait_for_jobs    = true
  atomic           = true
  cleanup_on_fail  = true

  values = [file("${path.module}/configurations/values.yaml")]

  set = [
    { name = "service.externalIPs[0]", value = var.eks_container_ip },
    # { name = "ports.web.nodePort", value = var.traefik_web_node_port },
    { name = "ports.${var.traefik_host_entry_point_name}.port", value = var.eks_container_host_port }, # to be matched
    # { name = "ports.${var.traefik_host_entry_point_name}.nodePort", value = var.eks_container_host_port }, # to be called
  ]
}