# INPUTS
locals {
  eks = var.eks
}
# COMPUTED
locals {
  # SYSTEM PORTS
  system_ports = {
    http = 80
    https = 443
  }
}
