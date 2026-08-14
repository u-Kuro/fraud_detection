# CONTROL PLANE
data "aws_iam_policy" "eks_cluster_policy" {
  name = "AmazonEKSClusterPolicy"
}
resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  role       = var.eks_role_name
  policy_arn = data.aws_iam_policy.eks_cluster_policy.arn
}
resource "aws_eks_cluster" "main" {
  name     = "EKS"
  version  = "1.32"
  role_arn = var.eks_role_arn

  vpc_config {
    subnet_ids = ["subnet-00000000000000000", "subnet-00000000000000001"]
  }

  depends_on = [aws_iam_role_policy_attachment.eks_cluster_policy]
}
# WORKER NODES
data "aws_iam_policy" "eks_worker_node_policy" {
  name = "AmazonEKSWorkerNodePolicy"
}
resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  role       = var.ec2_role_name
  policy_arn = data.aws_iam_policy.eks_worker_node_policy.arn
}
data "aws_iam_policy" "eks_cni_policy" {
  name = "AmazonEKS_CNI_Policy"
}
resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  role       = var.ec2_role_name
  policy_arn = data.aws_iam_policy.eks_cni_policy.arn
}
data "aws_iam_policy" "ecr_read_only" {
  name = "AmazonEC2ContainerRegistryReadOnly"
}
resource "aws_iam_role_policy_attachment" "ecr_read_only" {
  role       = var.ec2_role_name
  policy_arn = data.aws_iam_policy.ecr_read_only.arn
}
resource "aws_eks_node_group" "main" {
  cluster_name  = aws_eks_cluster.main.id
  node_role_arn = var.ec2_role_arn

  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 1
  }

  subnet_ids = ["subnet-00000000000000000", "subnet-00000000000000001"]

  depends_on = [
    aws_eks_cluster.main,
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.ecr_read_only,
  ]
}
# ADMIN CLUSTER PERMISSION
resource "aws_eks_access_entry" "admin" {
  cluster_name  = aws_eks_cluster.main.id
  principal_arn = var.iam_admin_role_arn
  type          = "STANDARD"

  depends_on = [aws_eks_cluster.main]
}
resource "aws_eks_access_policy_association" "admin" {
  cluster_name  = aws_eks_cluster.main.id
  principal_arn = var.iam_admin_role_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope { type = "cluster" }

  depends_on = [aws_eks_cluster.main]
}
# TEAMS' EKS CLUSTER PERMISSIONS
resource "aws_eks_access_entry" "teams" {
  for_each      = var.eks_teams
  cluster_name  = aws_eks_cluster.main.id
  principal_arn = var.iam_teams_role_arn[each.key]
  type          = "STANDARD"

  depends_on = [aws_eks_cluster.main]
}
resource "kubernetes_role_binding" "teams" {
  for_each = var.eks_teams

  metadata {
    name      = "${each.key}_ROLE_BINDING"
    namespace = var.eks_teams_namespace[each.key]
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "edit"
  }

  subject {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Group"
    name      = "${each.key}:team"
  }

  depends_on = [aws_eks_cluster.main]
}
# ADDITIONAL SETUP FOR MINISTACK EKS
resource "local_sensitive_file" "kubeconfig_container" {
  filename        = "${var.local_files_directory_path}/kubeconfig.yaml"
  file_permission = "0600"
}
resource "local_sensitive_file" "ecr_registries" {
  filename        = "${var.local_files_directory_path}/registries.yaml"
  file_permission = "0600"

  content = yamlencode({
    mirrors = {
      (var.ecr_aws_endpoint) = {
        endpoint = [var.ecr_container_endpoint_url]
      }
    }
    configs = {
      (var.ecr_container_endpoint) = {
        auth = {
          username = var.ecr_username
          password = var.ecr_password
        }
      }
    }
  })
}
resource "terraform_data" "additional_setup_for_ministack_eks" {
  depends_on = [aws_eks_cluster.main]

  # Re-run local-exec if cluster id changed
  triggers_replace = {
    cluster_id = aws_eks_cluster.main.id
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command = join(" ", [
      "& '${path.module}/scripts/additional_setup_for_ministack_eks.ps1'",

      "-aws_admin_access_key (ConvertTo-SecureString '${var.iam_admin_username}' -AsPlainText -Force)",
      "-aws_admin_secret_key (ConvertTo-SecureString '${var.iam_admin_password}' -AsPlainText -Force)",
      "-aws_admin_region '${var.iam_admin_region}'",

      "-eks_host_endpoint_url '${var.eks_host_endpoint_url}'",
      "-eks_cluster_name '${aws_eks_cluster.main.id}'",

      "-kubeconfig_container_file_path '${local_sensitive_file.kubeconfig_container.filename}'",
      "-kubeconfig_host_file_path '${var.local_files_kubeconfig_file_path}'",

      "-registries_host_file_path '${local_sensitive_file.ecr_registries.filename}'",
    ])
  }
}