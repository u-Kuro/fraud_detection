# TODO - 03/08/2026 - Continue here... Create N user team credentials and attach to policy. create teams and infos here in main instead of per module

locals {
  teams = {
    mle = {
      ecr_repositories = [
        "archive",
        "drift_check",
        "fraud_detection",
        "train_model",
      ]
    }
  }
}

module "iam" {
  source = "./modules/aws_iam"

  teams  = keys(local.teams)
}

module "ecr_repository" {
  source = "./modules/aws_ecr"

  teams = {
    for team, values in local.teams : team => {
      ecr_repositories  = values.ecr_repositories
      name              = module.iam.team_users[team].name
      arn               = module.iam.team_users[team].arn
    }
  }

  aws_account_id  = module.iam.admin_identity.account_id

  depends_on = [module.iam]
}

# Creates local EKS container from local AWS emulator (MiniStack)
# then Copies its k3s.yaml (kubeconfig)
# into Other local emulated services (e.g. MWAA)
# to Allow access to manage cluster resources
module "eks_cluster" {
  source = "./modules/aws_eks"

  admin_arn = module.iam.admin_identity.arn

  teams = {
    for team, values in module.iam.team_users : team => {
      arn = values.arn
    }
  }

  aws_access_key  = var.aws_access_key
  aws_secret_key  = var.aws_secret_key
  aws_region      = var.aws_region

  eks_service_endpoint_url = var.eks_service_endpoint_url

  kubeconfig_host_directory_path  = var.kubeconfig_host_directory_path
  kubeconfig_host_file_name       = var.kubeconfig_host_file_name

  ecr_registry_endpoint             = var.ecr_registry_endpoint
  ecr_registry_mirror_endpoint_url  = var.ecr_registry_mirror_endpoint_url
  ecr_registry_mirror_endpoint      = var.ecr_registry_mirror_endpoint

  ecr_registry_secret_name  = var.ecr_registry_secret_name
  ecr_registry_username     = var.ecr_registry_username
  ecr_registry_password     = var.ecr_registry_password

  depends_on = [module.iam]
}

module "rds_db" {
  source = "./modules/aws_rds"

  db_username = var.rds_db_username
  db_password = var.rds_db_password
}

module "s3" {
  source = "./modules/aws_s3"

  teams = {
    for team, values in module.iam.team_users : team => {
      name = values.name
    }
  }

  depends_on = [module.iam]
}

module "secrets_manager" {
  source = "./modules/aws_secrets_manager"

  teams = {
    for team, values in module.iam.team_users : team => {
      name = values.name
    }
  }
  aws_account_id = var.aws_account_id

  depends_on = [module.iam]
}

# Creates local MWAA container from local AWS emulator (MiniStack)
# then Copies kubeconfig (k3s.yaml from local EKS container)
# into its local container
# to Allow access to manage cluster resources
module "aws_mwaa_environment" {
  source = "./modules/aws_mwaa"

  aws_access_key  = var.aws_access_key
  aws_secret_key  = var.aws_secret_key
  aws_region      = var.aws_region

  eks_service_endpoint_url  = var.eks_service_endpoint_url
  eks_cluster_name          = module.eks_cluster.name

  s3_service_endpoint_url = var.s3_service_endpoint_url
  s3_mwaa_bucket_name     = module.s3.mwaa_bucket_name
  s3_mwaa_bucket_arn      = module.s3.mwaa_bucket_arn

  aws_account_id = var.aws_account_id

  secretsmanager_service_endpoint_url = var.secretsmanager_service_endpoint_url

  teams = {
    for team, values in local.teams : team => {
      name = module.iam.team_users[team].name
    }
  }

  depends_on = [
    module.iam,
    module.eks_cluster,
    module.s3
  ]
}

module "postgresql" {
  source = "./modules/postgresql"

  db_name           = module.rds_db.name
  db_owner_username = module.rds_db.username

  mlflow_postgresql_username  = var.mlflow_postgresql_username
  mlflow_postgresql_password  = var.mlflow_postgresql_password

  postgresql_teams = toset(keys(local.teams))

  depends_on = [
    module.rds_db
  ]
}

module "helm_apps" {
  source = "./modules/helm_apps"

  mlflow_user_name  = module.iam.mlflow_user.name
  mlflow_bucket_arn = module.s3.mlflow_bucket_arn

  rds_db_address  = module.rds_db.address
  rds_db_port     = module.rds_db.port
  rds_db_name     = module.rds_db.name

  s3_internal_endpoint_url    = var.s3_internal_endpoint_url
  s3_mlflow_bucket_aws_region = module.s3.mlflow_bucket_aws_region
  s3_mlflow_bucket            = module.s3.mlflow_bucket_name

  mlflow_db_username = module.postgresql.mlflow_username
  mlflow_db_password = module.postgresql.mlflow_password

  mlflow_access_key = module.iam.mlflow_access_key

  mlflow_teams = toset(keys(local.teams))

  depends_on = [
    module.iam,
    module.eks_cluster,
    module.rds_db,
    module.s3,
    module.postgresql,
  ]
}