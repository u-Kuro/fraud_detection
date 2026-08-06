# CONTROL PLANE
data "aws_iam_policy" "eks_cluster_policy" {
  name = "AmazonEKSClusterPolicy"
}
resource "aws_iam_role_policy_attachment" "eks" {
  role       = var.eks.role.name
  policy_arn = data.aws_iam_policy.eks_cluster_policy.arn
}
resource "aws_eks_cluster" "eks" {
  name     = "eks"
  version  = "1.32"
  role_arn = var.eks.role.arn

  vpc_config {
    security_group_ids = ["sg-00000000000000000"]
    subnet_ids         = ["subnet-00000000000000000", "subnet-00000000000000001"]
  }

  depends_on = [aws_iam_role_policy_attachment.eks]
}
# WORKER NODES
data "aws_iam_policy" "eks_worker_node_policy" {
  name = "AmazonEKSWorkerNodePolicy"
}
resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  role       = var.ec2.role.name
  policy_arn = data.aws_iam_policy.eks_worker_node_policy.arn
}
data "aws_iam_policy" "eks_cni_policy" {
  name = "AmazonEKS_CNI_Policy"
}
resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  role       = var.ec2.role.name
  policy_arn = data.aws_iam_policy.eks_cni_policy.arn
}
data "aws_iam_policy" "ecr_read_only" {
  name = "AmazonEC2ContainerRegistryReadOnly"
}
resource "aws_iam_role_policy_attachment" "ecr_read_only" {
  role       = var.ec2.role.name
  policy_arn = data.aws_iam_policy.ecr_read_only.arn
}
resource "aws_eks_node_group" "node" {
  cluster_name  = aws_eks_cluster.eks.id
  node_role_arn = var.ec2.role.arn

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
  principal_arn = var.aws_admin.arn
  type          = "STANDARD"

  depends_on = [aws_eks_cluster.eks]
}
resource "aws_eks_access_policy_association" "admin" {
  cluster_name  = aws_eks_cluster.eks.id
  principal_arn = var.aws_admin.arn
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
  principal_arn = each.value.role.arn
  type          = "STANDARD"

  depends_on = [aws_eks_cluster.eks]
}
resource "aws_eks_access_policy_association" "teams" {
  for_each      = var.teams
  cluster_name  = aws_eks_cluster.eks.id
  principal_arn = each.value.role.arn
  policy_arn    = local.cluster_access_policy_arns.edit

  access_scope {
    type       = "namespace"
    namespaces = [each.value.kubernetes.namespace]
  }

  depends_on = [
    aws_eks_cluster.eks,
    aws_eks_access_entry.teams
  ]
}
# ADDITIONAL SETUP FOR MINISTACK EKS
resource "local_sensitive_file" "kubeconfig_container" {
  filename        = "${var.local_files.directory.path}/kubeconfig.yaml"
  file_permission = "0600"
}
resource "local_sensitive_file" "ecr_registries" {
  filename        = "${var.local_files.directory.path}/registries.yaml"
  file_permission = "0600"

  content = yamlencode({
    mirrors = {
      (var.ecr.host.endpoint) = {
        endpoint = [var.ecr.container.endpoint_url]
      }
    }
    configs = {
      (var.ecr.container.endpoint) = {
        auth = {
          username = var.ecr.username
          password = var.ecr.password
        }
      }
    }
  })
}
resource "terraform_data" "additional_setup_for_ministack_eks" {
  depends_on = [aws_eks_cluster.eks]

  # Re-run local-exec if cluster id changed
  triggers_replace = {
    cluster_id = aws_eks_cluster.eks.id
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command = join(" ", [
      "& '${path.module}/scripts/additional_setup_for_ministack_eks.ps1'",

      "-aws_admin_access_key (ConvertTo-SecureString '${var.aws_admin.access_key}' -AsPlainText -Force)",
      "-aws_admin_secret_key (ConvertTo-SecureString '${var.aws_admin.secret_key}' -AsPlainText -Force)",
      "-aws_admin_region '${var.aws_admin.region}'",

      "-eks_host_endpoint_url '${var.eks.host.endpoint_url}'",
      "-eks_cluster_name '${aws_eks_cluster.eks.id}'",

      "-kubeconfig_container_file_path '${local_sensitive_file.kubeconfig_container.filename}'",
      "-kubeconfig_host_file_path '${var.kubeconfig.host.file.path}'",

      "-registries_host_file_path '${local_sensitive_file.ecr_registries.filename}'",
    ])
  }
}