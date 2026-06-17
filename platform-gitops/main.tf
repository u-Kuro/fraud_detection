module "ecr_repository" {
  source  = "./modules/aws_ecr"
  region  = var.aws_region
}

module "rds_db" {
  source      = "./modules/aws_rds"
  db_username = var.rds_db_username
  db_password = var.rds_db_password

}

module "postgresql" {
  source                     = "./modules/postgresql"
  db_owner_username          = module.rds_db.username
  db_name                    = module.rds_db.name
  mlflow_db_username         = var.mlflow_db_username
  mlflow_db_password         = var.mlflow_db_password
  mle_db_username            = var.mle_db_username
  mle_password               = var.mle_db_password
  mle_migrations_db_username = var.mle_migrations_db_username
  mle_migrations_db_password = var.mle_migrations_db_password
  depends_on  = [module.rds_db]
  providers   = { postgresql = postgresql }
}

module "s3" {
  source     = "./modules/aws_s3"
  aws_region = var.aws_region
}

# EKS: creates k3s cluster + runs extract-kubeconfig.ps1 automatically.
module "eks_cluster" {
  source                            = "./modules/aws_eks"
  aws_access_key                    = var.aws_access_key
  aws_secret_key                    = var.aws_secret_key
  aws_region                        = var.aws_region
  aws_account_id                    = var.aws_account_id
  eks_service_endpoint_url          = var.eks_service_endpoint_url
  ecr_registry_endpoint             = var.ecr_registry_endpoint
  ecr_registry_mirror_endpoint      = var.ecr_registry_mirror_endpoint
  ecr_registry_mirror_endpoint_url  = var.ecr_registry_mirror_endpoint_url
  ecr_registry_secret_name          = var.ecr_registry_secret_name
  kubeconfig_host_directory_path    = var.kubeconfig_host_directory_path
  kubeconfig_host_file_name         = var.kubeconfig_host_file_name
}

# Helm apps depend on EKS (kubeconfig must exist before Helm provider connects).
module "helm_apps" {
  source                      = "./modules/helm_apps"
  aws_access_key              = var.aws_access_key
  aws_secret_key              = var.aws_secret_key
  aws_account_id              = var.aws_account_id
  s3_internal_endpoint_url    = var.s3_internal_endpoint_url
  s3_mlflow_bucket_aws_region = module.s3.mlflow_bucket_aws_region
  s3_mlflow_bucket            = module.s3.mlflow_bucket_name
  s3_mle_bucket_aws_region    = module.s3.mle_bucket_aws_region
  s3_mle_bucket               = module.s3.mle_bucket_name
  rds_db_address              = module.rds_db.address
  rds_db_port                 = module.rds_db.port
  rds_db_name                 = module.rds_db.name
  mlflow_db_username          = module.postgresql.mlflow_db_username
  mlflow_db_password          = module.postgresql.mlflow_db_password

  depends_on = [
    module.rds_db,
    module.postgresql,
    module.s3,
    module.eks_cluster,
    module.ecr_repository
  ]
}

module "secrets_manager" {
  source                  = "./modules/aws_secrets_manager"
  rds_db_address          = module.rds_db.address
  rds_db_port             = module.rds_db.port
  rds_db_name             = module.rds_db.name
  mle_db_username         = module.postgresql.mle_db_username
  mle_db_password         = module.postgresql.mle_db_password
  s3_endpoint_url         = var.s3_internal_endpoint_url
  s3_access_key           = var.aws_access_key
  s3_secret_key           = var.aws_secret_key
  s3_aws_region           = var.aws_region
  s3_mle_bucket           = module.s3.mle_bucket_name
  s3_mlflow_bucket        = module.s3.mlflow_bucket_name
  mlflow_tracking_uri     = "http://mlflow:${5000}"
  fraud_api_url           = "http://fraud-detection:30000"
  slack_bot_token         = var.slack_bot_token
  slack_app_token         = var.slack_app_token
  slack_channel_id        = var.slack_channel_id
  slack_signing_secret    = var.slack_signing_secret

  depends_on = [
    module.rds_db,
    module.postgresql,
    module.s3,
    module.helm_apps
  ]
}

# MWAA depends on S3 (requirements.txt) and EKS (internal kubeconfig upload).
module "aws_mwaa_environment" {
  source                    = "./modules/aws_mwaa"
  aws_access_key            = var.aws_access_key
  aws_secret_key            = var.aws_secret_key
  aws_region                = var.aws_region
  aws_account_id            = var.aws_account_id
  eks_service_endpoint_url  = var.eks_service_endpoint_url
  s3_service_endpoint_url   = var.s3_service_endpoint_url
  s3_mle_bucket             = module.s3.mle_bucket_name
  eks_cluster_name          = module.eks_cluster.name
  mle_db_username           = module.postgresql.mle_db_username
  mle_db_password           = module.postgresql.mle_db_password
  rds_db_address            = module.rds_db.address
  rds_db_name               = module.rds_db.name

  depends_on = [
    module.s3,
    module.eks_cluster,
    module.helm_apps
  ]
}