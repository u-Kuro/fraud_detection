resource "aws_iam_role" "eks" {
  name = "eks_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
      Action    = "sts:AssumeRole"
    }]
  })
}
resource "aws_iam_role_policy_attachment" "eks" {
  role       = aws_iam_role.eks.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"

  depends_on = [aws_iam_role.eks]
}
resource "aws_eks_cluster" "eks" {
  name      = "eks"
  version   = "1.32"
  role_arn  = aws_iam_role.eks.arn

  vpc_config {
    security_group_ids  = ["sg-00000000000000000"]
    subnet_ids          = ["subnet-00000000000000000", "subnet-00000000000000001"]
  }

  depends_on = [aws_iam_role.eks]
}

resource "aws_iam_role" "node" {
  name = "eks_node_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}
resource "aws_iam_role_policy_attachment" "node_worker" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"

  depends_on = [aws_iam_role.node]
}
resource "aws_iam_role_policy_attachment" "node_cni" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"

  depends_on = [aws_iam_role.node]
}
resource "aws_iam_role_policy_attachment" "node_ecr" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"

  depends_on = [aws_iam_role.node]
}
resource "aws_eks_node_group" "node" {
  cluster_name    = aws_eks_cluster.eks.name
  node_group_name = "node"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = ["subnet-00000000000000000", "subnet-00000000000000001"]

  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 1
  }

  depends_on = [
    aws_iam_role_policy_attachment.node_worker,
    aws_iam_role_policy_attachment.node_cni,
    aws_iam_role_policy_attachment.node_ecr,
    aws_eks_cluster.eks
  ]
}

resource "aws_eks_access_entry" "admin" {
  cluster_name  = aws_eks_cluster.eks.name
  principal_arn = var.admin_arn
  type          = "STANDARD"

  depends_on = [aws_eks_cluster.eks]
}
resource "aws_eks_access_policy_association" "admin" {
  cluster_name  = aws_eks_cluster.eks.name
  principal_arn = var.admin_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }

  depends_on = [aws_eks_cluster.eks]
}

resource "aws_eks_access_entry" "teams" {
  for_each      = var.teams
  cluster_name  = aws_eks_cluster.eks.name
  principal_arn = each.value.arn
  type          = "STANDARD"

  depends_on = [aws_eks_cluster.eks]
}
resource "aws_eks_access_policy_association" "teams" {
  for_each      = aws_eks_access_entry.teams
  cluster_name  = each.value.cluster_name
  principal_arn = each.value.principal_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy"

  access_scope {
    type       = "namespace"
    namespaces = [each.key]
  }

  depends_on = [aws_eks_access_entry.teams]
}

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
      "-eks_cluster_name '${aws_eks_cluster.eks.name}'",

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