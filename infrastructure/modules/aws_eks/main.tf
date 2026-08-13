# CONTROL PLANE
data "aws_iam_policy" "eks_cluster_policy" {
  name = "AmazonEKSClusterPolicy"
}
resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  role       = local.eks.role.name
  policy_arn = data.aws_iam_policy.eks_cluster_policy.arn
}
resource "aws_eks_cluster" "main" {
  name     = "EKS"
  version  = "1.32"
  role_arn = local.eks.role.arn

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
  role       = local.ec2.role.name
  policy_arn = data.aws_iam_policy.eks_worker_node_policy.arn
}
data "aws_iam_policy" "eks_cni_policy" {
  name = "AmazonEKS_CNI_Policy"
}
resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  role       = local.ec2.role.name
  policy_arn = data.aws_iam_policy.eks_cni_policy.arn
}
data "aws_iam_policy" "ecr_read_only" {
  name = "AmazonEC2ContainerRegistryReadOnly"
}
resource "aws_iam_role_policy_attachment" "ecr_read_only" {
  role       = local.ec2.role.name
  policy_arn = data.aws_iam_policy.ecr_read_only.arn
}
resource "aws_eks_node_group" "main" {
  cluster_name  = aws_eks_cluster.main.id
  node_role_arn = local.ec2.role.arn

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
  principal_arn = local.iam.users.admin.arn
  type          = "STANDARD"

  depends_on = [aws_eks_cluster.main]
}
resource "aws_eks_access_policy_association" "admin" {
  cluster_name  = aws_eks_cluster.main.id
  principal_arn = local.iam.users.admin.arn
  policy_arn    = local.cluster_access_policy_arns.cluster_admin

  access_scope { type = "cluster" }

  depends_on = [aws_eks_cluster.main]
}
# TEAMS' EKS CLUSTER PERMISSIONS
resource "aws_eks_access_entry" "teams" {
  for_each      = local.eks.users.teams
  cluster_name  = aws_eks_cluster.main.id
  principal_arn = local.iam.users.teams[each.key].arn
  type          = "STANDARD"

  depends_on = [aws_eks_cluster.main]
}
resource "kubernetes_role_binding" "teams" {
  for_each = local.eks.users.teams

  metadata {
    name      = "${each.key}_ROLE_BINDING"
    namespace = local.eks_users.teams[each.key].kubernetes.namespace
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
  filename        = "${local.local_files.directory.path}/kubeconfig.yaml"
  file_permission = "0600"
}
resource "local_sensitive_file" "ecr_registries" {
  filename        = "${local.local_files.directory.path}/registries.yaml"
  file_permission = "0600"

  content = yamlencode({
    mirrors = {
      (local.ecr.aws.endpoint) = {
        endpoint = [local.ecr.container.endpoint_url]
      }
    }
    configs = {
      (local.ecr.container.endpoint) = {
        auth = {
          username = local.ecr.username
          password = local.ecr.password
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

      "-aws_admin_access_key (ConvertTo-SecureString '${local.iam.users.admin.username}' -AsPlainText -Force)",
      "-aws_admin_secret_key (ConvertTo-SecureString '${local.iam.users.admin.password}' -AsPlainText -Force)",
      "-aws_admin_region '${local.iam.users.admin.region}'",

      "-eks_host_endpoint_url '${local.eks.host.endpoint_url}'",
      "-eks_cluster_name '${aws_eks_cluster.main.id}'",

      "-kubeconfig_container_file_path '${local_sensitive_file.kubeconfig_container.filename}'",
      "-kubeconfig_host_file_path '${local.local_files.kubeconfig.host.file.path}'",

      "-registries_host_file_path '${local_sensitive_file.ecr_registries.filename}'",
    ])
  }
}