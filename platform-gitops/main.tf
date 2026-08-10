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

  teams = keys(local.teams)
}

module "ecr_repository" {
  source = "./modules/aws_ecr"

  teams = {
    for team, values in local.teams : team => {
      ecr_repositories = values.ecr_repositories
      role_arn         = module.iam.teams[team].role.arn
    }
  }

  admin_aws_account_id = module.iam.admin.account_id

  depends_on = [module.iam]
}

# Creates local EKS container from local AWS emulator (MiniStack)
# then Copies its k3s.yaml (kubeconfig)
# into Other local emulated services (e.g. MWAA)
# to Allow access to manage cluster resources
module "eks_cluster" {
  source = "./modules/aws_eks"

  aws_admin = module.iam.admin.arn

  teams = {
    for team, values in module.iam.team_users : team => {
      arn = values.arn
    }
  }

  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
  aws_region     = var.aws_region

  eks_service_endpoint_url = var.eks_host_endpoint_url

  local_files_directory_path = local.local_files_directory_path
  kubeconfig_host_file_name  = var.kubeconfig_host_file_name

  ecr_registry_endpoint            = var.ecr_host_registry_endpoint
  ecr_registry_mirror_endpoint_url = var.ecr_container_endpoint_url
  ecr_registry_mirror_endpoint     = var.ecr_container_endpoint

  ecr_registry_secret_name = var.ecr_secret_name
  ecr_registry_username    = var.ecr_username
  ecr_registry_password    = var.ecr_password

  depends_on = [
    local_file.kubeconfig_file,
    module.iam
  ]
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

  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
  aws_region     = var.aws_region

  eks_service_endpoint_url = var.eks_host_endpoint_url
  eks_cluster_name         = module.eks_cluster.name

  s3_service_endpoint_url = var.s3_host_endpoint_url
  s3_mwaa_bucket_name     = module.s3.mwaa_bucket_name
  s3_mwaa_bucket_arn      = module.s3.mwaa_bucket_arn

  aws_account_id = var.aws_account_id

  secretsmanager_service_endpoint_url = var.secretsmanager_host_endpoint_url

  teams = {
    for team, values in local.teams : team => {
      name = module.iam.team_users[team].name
    }
  }

  kubeconfig_file_path = local_file.kubeconfig_file.filename

  depends_on = [
    module.iam,
    module.eks_cluster,
    module.s3,
    local_file.kubeconfig_file
  ]
}

module "postgresql" {
  source = "./modules/postgresql"

  db_name           = module.rds_db.name
  db_owner_username = module.rds_db.username

  mlflow_postgresql_username = var.mlflow_postgresql_username
  mlflow_postgresql_password = var.mlflow_postgresql_password

  postgresql_teams = toset(keys(local.teams))

  depends_on = [
    module.rds_db
  ]
}

module "aws_alb" {
  source = "modules/aws_lb"

  depends_on = [module.eks_cluster]
}

module "mlflow" {
  source = "modules/mlflow"

  mlflow_user_name  = module.iam.mlflow_user.name
  mlflow_bucket_arn = module.s3.mlflow_bucket_arn

  rds_db_address = module.rds_db.address
  rds_db_port    = module.rds_db.port
  rds_db_name    = module.rds_db.name

  s3_internal_endpoint_url    = var.s3_container_endpoint_url
  s3_mlflow_bucket_aws_region = module.s3.mlflow_bucket_aws_region
  s3_mlflow_bucket            = module.s3.mlflow_bucket_name

  mlflow_db_username = module.postgresql.mlflow_username
  mlflow_db_password = module.postgresql.mlflow_password

  aws_admin = module.iam.mlflow_access_key

  mlflow_teams = toset(keys(local.teams))

  alb = {
    listener_arn = module.aws_alb.listener_arn
    vpc_id       = module.aws_alb.vpc_id
    dns_name     = module.aws_alb.alb_dns_name
  }

  depends_on = [
    module.iam,
    module.eks_cluster,
    module.rds_db,
    module.s3,
    module.postgresql,
  ]
}