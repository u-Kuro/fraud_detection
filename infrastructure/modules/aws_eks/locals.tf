locals {
  # EKS
  # /teams
  eks_teams_namespaces = { for k in var.eks_teams : k => k }

  # Local Files
  # /base64
  base64_kubeconfig_for_localhost_file_path = filebase64(data.external.k3s_configuration.result.kubeconfig_for_localhost_file_path)
}