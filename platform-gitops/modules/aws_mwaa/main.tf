locals {
  dag_s3_path                     = "dags"
  requirements_file_name          = "requirements.txt"
  temporary_kubeconfig_file_path  = "$env:TEMP\\airflow_kubeconfig.yaml"
  airflow_kubeconfig_s3_uri       = "s3://${var.s3_dags_bucket}/${local.dag_s3_path}/kubeconfig.yaml"
}

# Airflow needs this provider installed to run KubernetesPodOperator.
resource "aws_s3_object" "requirements" {
  bucket  = var.s3_dags_bucket
  key     = local.requirements_file_name
  content = "apache-airflow-providers-cncf-kubernetes\n"
}

# Upload the Docker-internal kubeconfig to S3 so Airflow can mount it.
# This kubeconfig uses the k3s container DNS name as the server URL —
# correct from inside ministack_network where Airflow runs, but NOT
# from the Windows host (that version lives in /kubeconfig/k3s.yaml).
resource "terraform_data" "upload_airflow_kubeconfig" {
  triggers_replace = {
    eks_cluster_name = var.eks_cluster_name
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command     = join(" ", [
      "& '${path.module}/scripts/upload-airflow-kubeconfig.ps1'",
      "-cluster_name '${var.eks_cluster_name}'",
      "-eks_service_endpoint_url '${var.eks_service_endpoint_url}'",
      "-s3_service_endpoint_url '${var.s3_service_endpoint_url}'",
      "-temporary_kubeconfig_file_path '${local.temporary_kubeconfig_file_path}'",
      "-airflow_kubeconfig_s3_uri '${local.airflow_kubeconfig_s3_uri}'"
    ])
  }
}

resource "aws_mwaa_environment" "main" {
  name                  = var.environment_name
  airflow_version       = "2.10.3"
  source_bucket_arn     = "arn:aws:s3:::${var.s3_dags_bucket}"
  execution_role_arn    = "arn:aws:iam::${var.aws_account_id}:role/mwaa-role"

  dag_s3_path           = "${local.dag_s3_path}/"
  requirements_s3_path  = local.requirements_file_name

  network_configuration {
    security_group_ids = ["sg-00000000000000001"]
    subnet_ids         = ["subnet-00000000000000001", "subnet-00000000000000002"]
  }

  depends_on = [
    aws_s3_object.requirements,
    terraform_data.upload_airflow_kubeconfig
  ]
}
