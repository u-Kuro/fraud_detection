# INPUTS
locals {
  iam         = var.iam
  ec2         = var.ec2
  ecr         = var.ecr
  eks         = var.eks
  local_files = var.local_files
  ssm_parameter = var.ssm_parameter
}
# COMPUTED
locals {
  # EKS CLUSTER
  eks_users = {
    teams = {
      for k, v in local.eks.users.teams : k => {
        kubernetes = {
          namespace = v.metadata[0].namespace
        }
      }
    }
  }
  # EKS CLUSTER PERMISSIONS
  _cluster_access_policy_arn_ = "arn:aws:eks::aws:cluster-access-policy"
  cluster_access_policy_arns = {
    cluster_admin = "${local._cluster_access_policy_arn_}/AmazonEKSClusterAdminPolicy"
  }
}