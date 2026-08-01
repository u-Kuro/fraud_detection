resource "aws_eks_cluster" "main" {
  name      = "eks"
  role_arn  = "arn:aws:iam::${var.aws_account_id}:role/eks"
  version   = "1.32"

  vpc_config {
    security_group_ids  = ["sg-00000000000000000"]
    subnet_ids          = ["subnet-00000000000000000", "subnet-00000000000000001"]
  }
}

resource "terraform_data" "init" {
  depends_on = [aws_eks_cluster.main]

  # Re-run local-exec if cluster id changed
  triggers_replace = {
    cluster_id = aws_eks_cluster.main.id
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command     = join(" ", [
      "& '${path.module}/scripts/initialize-ministack-k3s.ps1'",

      "-aws_access_key '${var.aws_access_key}'",
      "-aws_secret_key '${var.aws_secret_key}'",
      "-aws_region '${var.aws_region}'",

      "-eks_service_endpoint_url '${var.eks_service_endpoint_url}'",
      "-eks_cluster_name '${aws_eks_cluster.main.name}'",

      "-kubeconfig_host_directory_path '${var.kubeconfig_host_directory_path}'",
      "-kubeconfig_host_file_name '${var.kubeconfig_host_file_name}'",

      "-ecr_registry_endpoint '${var.ecr_registry_endpoint}'",
      "-ecr_registry_mirror_endpoint_url '${var.ecr_registry_mirror_endpoint_url}'",
      "-ecr_registry_mirror_endpoint '${var.ecr_registry_mirror_endpoint}'",

      "-ecr_registry_secret_name '${var.ecr_registry_secret_name}'",
    ])
  }
}

# ── EKS Access Entries — map IAM Role → Kubernetes group ─────────────────────
# When the team's IAM Role authenticates to the cluster, Kubernetes sees it as
# a member of "<team>-group". The actual RBAC bindings are in kubernetes_resources.
# MiniStack: simulated — the entry is stored; the k3s cluster uses the kubeconfig
# directly and does not validate IAM identity, so this is a no-op locally but
# is required for production EKS.
resource "aws_eks_access_entry" "team" {
  for_each = var.team_role_arns

  cluster_name  = aws_eks_cluster.main.name
  principal_arn = each.value
  type          = "STANDARD"

  kubernetes_groups = ["${each.key}-group"]
}