# INPUTS
locals {
  aws         = var.aws
  ec2         = var.ec2
  ecr         = var.ecr
  eks         = var.eks
  local_files = var.local_files
}
# COMPUTED
locals {
  # CLUSTER PERMISSIONS
  _cluster_access_policy_arn_ = "arn:aws:eks::aws:cluster-access-policy"
  cluster_access_policy_arns = {
    cluster_admin = "${local._cluster_access_policy_arn_}/AmazonEKSClusterAdminPolicy"
    edit          = "${local._cluster_access_policy_arn_}/AmazonEKSEditPolicy"
  }
}