locals {
  # EKS
  # /teams
  eks_teams_namespaces = { for k in var.eks_teams : k => k }
}