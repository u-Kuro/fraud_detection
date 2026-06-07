module "ecr" {
  source          = "./modules/ecr"
  repository_name = var.ecr_repository_name
}

module "rds" {
  source      = "./modules/rds"
  db_name     = var.rds_db_name
  db_username = var.rds_db_username
  db_password = var.rds_db_password
}

module "s3" {
  source                  = "./modules/s3"
  dags_bucket_name             = var.s3_dags_bucket
  mlflow_artifacts_bucket_name = var.s3_mlflow_artifacts_bucket
}

# EKS: creates k3s cluster + runs extract-kubeconfig.ps1 automatically.
module "eks" {
  source       = "./modules/eks"
  cluster_name = var.eks_cluster_name
  kubeconfig_host_directory_path = "${path.root}/kubeconfig"
  k3s_mount_directory_path = "/etc/rancher/k3s"
  kubeconfig_mount_file_name = "k3s.yaml"

  depends_on = [module.rds]
}

# MWAA depends on S3 (requirements.txt) and EKS (internal kubeconfig upload).
module "mwaa" {
  source       = "./modules/mwaa"
  env_name     = "local-airflow"
  eks_cluster_name = var.eks_cluster_name
  s3_dags_bucket  = var.s3_dags_bucket

  depends_on = [
    module.s3,
    module.eks
  ]
}

# Helm apps depend on EKS (kubeconfig must exist before Helm provider connects).
module "helm_apps" {
  source = "./modules/helm_apps"

  rds_host        = module.rds.endpoint
  db_name         = var.rds_db_name
  db_username     = var.rds_db_username
  db_password     = var.rds_db_password
  mlflow_bucket   = var.s3_mlflow_artifacts_bucket
  slack_bot_token = var.slack_bot_token
  slack_app_token = var.slack_app_token

  depends_on = [
    module.eks,
    module.rds
  ]
}