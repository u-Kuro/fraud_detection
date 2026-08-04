# CONTROL PLANE
data "aws_iam_policy" "eks_cluster_policy" {
  name = "AmazonEKSClusterPolicy"
}
resource "aws_iam_role_policy_attachment" "eks" {
  role       = var.services_role.eks.name
  policy_arn = data.aws_iam_policy.eks_cluster_policy.arn
}
resource "aws_eks_cluster" "eks" {
  name      = "eks"
  version   = "1.32"
  role_arn  = var.services_role.eks.arn

  vpc_config {
    security_group_ids  = ["sg-00000000000000000"]
    subnet_ids          = ["subnet-00000000000000000", "subnet-00000000000000001"]
  }

  depends_on = [aws_iam_role_policy_attachment.eks]
}
# WORKER NODES
data "aws_iam_policy" "eks_worker_node_policy" {
  name = "AmazonEKSWorkerNodePolicy"
}
resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  role       = var.services_role.ec2.name
  policy_arn = data.aws_iam_policy.eks_worker_node_policy.arn
}
data "aws_iam_policy" "eks_cni_policy" {
  name = "AmazonEKS_CNI_Policy"
}
resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  role       = var.services_role.ec2.name
  policy_arn = data.aws_iam_policy.eks_cni_policy.arn
}
data "aws_iam_policy" "ecr_read_only" {
  name = "AmazonEC2ContainerRegistryReadOnly"
}
resource "aws_iam_role_policy_attachment" "ecr_read_only" {
  role       = var.services_role.ec2.name
  policy_arn = data.aws_iam_policy.ecr_read_only.arn
}
resource "aws_eks_node_group" "node" {
  cluster_name    = aws_eks_cluster.eks.id
  node_role_arn   = var.services_role.ec2.arn

  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 1
  }

  subnet_ids = ["subnet-00000000000000000", "subnet-00000000000000001"]

  depends_on = [
    aws_eks_cluster.eks,
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.ecr_read_only,
  ]
}
# CLUSTER PERMISSIONS
locals {
  cluster_access_policy_arn = "arn:aws:eks::aws:cluster-access-policy"
  cluster_access_policy_arns = {
    cluster_admin = "${local.cluster_access_policy_arn}/AmazonEKSClusterAdminPolicy"
    edit          = "${local.cluster_access_policy_arn}/AmazonEKSEditPolicy"
  }
}
# ADMIN CLUSTER PERMISSION
resource "aws_eks_access_entry" "admin" {
  cluster_name  = aws_eks_cluster.eks.id
  principal_arn = var.admin_arn
  type          = "STANDARD"

  depends_on = [aws_eks_cluster.eks]
}
resource "aws_eks_access_policy_association" "admin" {
  cluster_name  = aws_eks_cluster.eks.id
  principal_arn = var.admin_arn
  policy_arn    = local.cluster_access_policy_arns.cluster_admin

  access_scope { type = "cluster" }

  depends_on = [
    aws_eks_cluster.eks,
    aws_eks_access_entry.admin
  ]
}
# TEAM CLUSTER PERMISSIONS
resource "aws_eks_access_entry" "teams" {
  for_each      = var.teams
  cluster_name  = aws_eks_cluster.eks.id
  principal_arn = each.value.role_arn
  type          = "STANDARD"

  depends_on = [aws_eks_cluster.eks]
}
resource "aws_eks_access_policy_association" "teams" {
  for_each      = var.teams
  cluster_name  = aws_eks_cluster.eks.id
  principal_arn = each.value.role_arn
  policy_arn    = local.cluster_access_policy_arns.edit

  access_scope {
    type       = "namespace"
    namespaces = [each.value.namespace]
  }

  depends_on = [
    aws_eks_cluster.eks,
    aws_eks_access_entry.teams
  ]
}
# INITIALIZATION FOR MINISTACK
resource "terraform_data" "initialize_eks_cluster" {
  depends_on = [aws_eks_cluster.eks]

  # Re-run local-exec if cluster id changed
  triggers_replace = {
    cluster_id = aws_eks_cluster.eks.id
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command     = join(" ", [
      "& '${path.module}/scripts/initialize_eks_cluster.ps1'",

      "-aws_access_key '${var.aws_access_key}'",
      "-aws_secret_key '${var.aws_secret_key}'",
      "-aws_region '${var.aws_region}'",

      "-eks_service_endpoint_url '${var.eks_service_endpoint_url}'",
      "-eks_cluster_name '${aws_eks_cluster.eks.id}'",

      "-kubeconfig_host_directory_path '${var.kubeconfig_host_directory_path}'",
      "-kubeconfig_host_file_name '${var.kubeconfig_host_file_name}'",

      "-ecr_registry_endpoint '${var.ecr_registry_endpoint}'",
      "-ecr_registry_mirror_endpoint_url '${var.ecr_registry_mirror_endpoint_url}'",
      "-ecr_registry_mirror_endpoint '${var.ecr_registry_mirror_endpoint}'",

      "-ecr_registry_secret_name '${var.ecr_registry_secret_name}'",
      "-ecr_registry_username '${var.ecr_registry_username}'",
      "-ecr_registry_password '${var.ecr_registry_password}'",
    ])
  }
}