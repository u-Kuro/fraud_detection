resource "aws_eks_cluster" "eks" {
  name     = var.cluster_name
  role_arn = "arn:aws:iam::000000000000:role/eks"
  version  = "1.32"

  vpc_config {
    subnet_ids = [
      "subnet-00000000000000000",
      "subnet-00000000000000001",
    ]
  }
}

resource "terraform_data" "init" {
  depends_on = [aws_eks_cluster.eks]

  # Re-run local-exec if cluster id changed
  triggers_replace = {
    cluster_id = aws_eks_cluster.eks.id
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command     = join(" ", [
      "& '${path.module}/scripts/init.ps1'",
      "-cluster_name '${var.cluster_name}'",
      "-kubeconfig_host_directory_path '${var.kubeconfig_host_directory_path}'",
      "-k3s_mount_directory_path '${var.k3s_mount_directory_path}'",
      "-kubeconfig_mount_file_name '${var.kubeconfig_mount_file_name}'"
    ])
  }
}