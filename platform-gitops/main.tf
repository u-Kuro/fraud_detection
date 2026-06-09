module "ecr_repository" {
  source          = "./modules/aws_ecr"
  repository_name = var.ecr_repository_name
}

module "rds_db" {
  source      = "./modules/aws_rds"
  db_identifier = var.rds_db_identifier
  db_username   = var.rds_db_username
  db_password   = var.rds_db_password
}

module "s3" {
  source              = "./modules/aws_s3"
  dags_bucket_name    = var.s3_dags_bucket_name
  mlflow_bucket_name  = var.s3_mlflow_bucket_name
}

# EKS: creates k3s cluster + runs extract-kubeconfig.ps1 automatically.
module "eks_cluster" {
  source                            = "./modules/aws_eks"
  cluster_name                      = var.eks_cluster_name
  aws_account_id                    = var.aws_account_id
  eks_service_endpoint_url          = var.eks_service_endpoint_url
  ecr_registry_endpoint             = var.ecr_registry_endpoint
  ecr_registry_mirror_endpoint      = var.ecr_registry_mirror_endpoint
  ecr_registry_mirror_endpoint_url  = var.ecr_registry_mirror_endpoint_url
  kubeconfig_host_directory_path    = var.kubeconfig_host_directory_path
  k3s_mount_directory_path          = "/etc/rancher/k3s"
  k3s_mount_file_name               = var.k3s_mount_file_name

  depends_on = [module.rds_db]
}

# MWAA depends on S3 (requirements.txt) and EKS (internal kubeconfig upload).
module "aws_mwaa_environment" {
  source                    = "./modules/aws_mwaa"
  environment_name          = var.mwaa_environment_name
  aws_account_id            = var.aws_account_id
  eks_service_endpoint_url  = var.eks_service_endpoint_url
  s3_service_endpoint_url   = var.s3_service_endpoint_url
  s3_dags_bucket            = module.s3.dags_bucket_name
  eks_cluster_name          = module.eks_cluster.name

  depends_on = [
    module.s3,
    module.eks_cluster
  ]
}

# Helm apps depend on EKS (kubeconfig must exist before Helm provider connects).
module "helm_apps" {
  source                            = "./modules/helm_apps"
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
  aws_region = var.aws_region
  s3_internal_endpoint_url  = var.s3_internal_endpoint_url
  slack_bot_token                   = var.slack_bot_token
  slack_app_token           = var.slack_app_token
  s3_mlflow_bucket_name             = module.s3.mlflow_bucket_name
  rds_db_address                    = module.rds_db.address
  rds_db_port                       = module.rds_db.port
  rds_db_name                       = module.rds_db.name
  rds_db_username                   = module.rds_db.username
  rds_db_password                   = module.rds_db.password

  depends_on = [
    module.rds_db,
    module.s3,
    module.eks_cluster
  ]
}
