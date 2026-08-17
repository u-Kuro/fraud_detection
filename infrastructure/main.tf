locals {
  teams = {
    mle = {
      includes = {
        ecr             = true
        eks             = true
        mwaa            = true
        s3              = true
        secrets_manager = true
        ssm             = true
        mlflow          = true
        postgres      = true
      }
    }
  }
}

module "iam" {
  source = "./modules/aws_iam"

  iam_teams = keys(local.teams)
}

module "ssm" {
  source = "modules/aws_ssm"

  iam_admin_account_id = module.iam.admin_account_id
  iam_teams_names = module.iam.teams_names
  ssm_teams = local.ssm_teams

  depends_on = [module.iam]
}

module "s3" {
  source = "./modules/aws_s3"

  iam_teams_names = module.iam.teams_names
  mwaa_teams = local.mwaa_teams
  s3_teams = local.s3_teams

  depends_on = [module.iam]
}

module "rds" {
  source = "./modules/aws_rds"

  rds_role_name          = module.iam.rds_role_name
  rds_postgres_admin_username  = var.rds_postgres_admin_username
  rds_postgres_admin_password  = var.rds_postgres_admin_password
  s3_postgres_bucket_arn = module.s3.postgres_bucket_arn

  depends_on = [
    module.iam,
    module.s3
  ]
}
module "secrets_manager" {
  source = "./modules/aws_secrets_manager"

  iam_admin_account_id = module.iam.admin_account_id
  iam_teams_names = module.iam.teams_names
  secrets_manager_teams = local.secrets_manager_teams

  depends_on = [module.iam]
}
module "postgres" {
  source = "./modules/postgresql"

  rds_postgres_db_name         = module.rds.postgres_db_name
  rds_postgres_admin_username  = module.rds.postgres_admin_username
  rds_postgres_mlflow_username = var.rds_postgres_mlflow_username
  rds_postgres_mlflow_password = var.rds_postgres_mlflow_password
  rds_postgres_teams = local.rds_postgres_teams
  secrets_manager_teams_secret_paths = module.secrets_manager.teams_secret_path
  ssm_teams_parameter_paths = module.ssm.teams_parameter_path

  depends_on = [
    module.rds
  ]
}



module "ecr" {
  source = "./modules/aws_ecr"

  iam_admin_account_id = module.iam.admin_account_id
  iam_teams_names = module.iam.teams_names
  ecr_teams = local.ecr_teams

  depends_on = [module.iam]
}

# Creates local EKS container from local AWS emulator (MiniStack)
# then Copies its k3s.yaml (kubeconfig)
# into Other local emulated services (e.g. MWAA)
# to Allow access to manage cluster resources
module "eks" {
  source = "./modules/aws_eks"


  ec2_role_arn                          = module.iam.ec2_role_arn
  ec2_role_name                         = module.iam.ec2_role_name
  ecr_aws_endpoint                      = local.ecr_aws_endpoint
  ecr_container_endpoint                = var.ecr_container_endpoint
  ecr_container_endpoint_url            = var.ecr_container_endpoint_url
  ecr_password                          = local.ecr_password
  ecr_username                          = local.ecr_username
  eks_host_endpoint_url                 = var.eks_host_endpoint_url
  eks_role_arn                          = module.iam.eks_role_arn
  eks_role_name                         = module.iam.ec2_role_name
  eks_teams = local.eks_teams
  iam_admin_password                    = var.aws_admin_secret_key
  iam_admin_region                      = module.iam.admin_region
  iam_admin_arn                    = module.iam.admin_arn
  iam_admin_username                    = var.aws_admin_access_key
  iam_teams_role_arns = module.iam.teams_role_arns
  local_files_directory_path            = local.local_files_directory_path
  local_files_kubeconfig_host_file_path = local_sensitive_file.kubeconfig_host.filename
  ssm_teams_parameter_path = module.ssm.teams_parameter_path
  depends_on = [
    module.iam,
    local_sensitive_file.kubeconfig_host
  ]
}

module "elb" {
  source = "modules/aws_elb"

  eks_ip = module.eks.cluster_ip

  depends_on = [module.eks]
}

# Creates local MWAA container from local AWS emulator (MiniStack)
# then Copies kubeconfig (k3s.yaml from local EKS container)
# into its local container
# to Allow access to manage cluster resources
module "mwaa" {
  source = "./modules/aws_mwaa"


  iam_admin_account_id                       = module.iam.admin_account_id
  iam_teams_names = module.iam.teams_names
  iam_teams_role_arns = module.iam.teams_role_arns
  local_files_kubeconfig_container_file_path = module.eks.local_files_kubeconfig_container_path
  local_files_mwaa_requirements_file_path    = local_sensitive_file.mwaa_requirements.filename
  ministack_ip                               = local.ministack_container_ip
  ministack_port                             = number(local.ministack_container_host_port)
  mwaa_teams = local.mwaa_teams
  s3_teams_mwaa_bucket_arn                   = module.s3.teams_mwaa_bucket_arns
  s3_teams_mwaa_bucket_name                  = module.s3.teams_mwaa_bucket_names
  secrets_manager_container_endpoint_url     = local.secrets_manager_container_endpoint_url
  ssm_teams_parameter_path = module.ssm.teams_parameter_path

  depends_on = [
    module.iam,
    local_sensitive_file.mwaa_requirements,
    module.eks,
    module.s3
  ]
}

module "mlflow" {
  source = "modules/mlflow"

  elb_alb_dns_name                   = module.elb.alb_dns_name
  iam_admin_password                 = var.aws_admin_secret_key
  iam_admin_region                   = module.iam.admin_region
  iam_admin_username                 = var.aws_admin_access_key
  mlflow_admin_password              = var.mlflow_admin_password
  mlflow_admin_username              = var.mlflow_admin_username
  mlflow_flask_server_secret_key     = var.mlflow_flask_server_secret_key
  mlflow_teams                       = local.mlflow_teams
  rds_postgres_db_name               = module.rds.postgres_db_name
  rds_postgres_host                  = module.rds.postgres_host
  rds_postgres_mlflow_password       = var.rds_postgres_mlflow_password
  rds_postgres_mlflow_username       = var.rds_postgres_mlflow_username
  rds_postgres_port                  = module.rds.postgres_port
  s3_mlflow_bucket_arn               = module.s3.mlflow_bucket_arn
  s3_mlflow_bucket_name              = module.s3.mlflow_bucket_name
  secrets_manager_teams_secret_paths = module.secrets_manager.teams_secret_path
  ssm_teams_parameter_paths          = module.ssm.teams_parameter_path

  depends_on = [
    module.iam,
    module.elb,
    module.rds,
    module.s3
  ]
}

module "service_resources" {
  source = "modules/service_resources"

  ecr_aws_authorization_token          = local.ecr_authorization_token
  ecr_aws_authorization_token_password = local.ecr_password
  ecr_aws_authorization_token_username = local.ecr_username
  ecr_aws_endpoint                     = local.ecr_aws_endpoint
  eks_teams = module.eks.cluster_teams
  eks_teams_kubernetes_namespaces = module.eks.cluster_teams_namespaces
  iam_admin_region                     = module.iam.admin_region
  iam_teams_passwords = module.iam.teams_passwords
  iam_teams_usernames = module.iam.teams_usernames
  mlflow_inter_url                     = module.mlflow.inter_url
  mlflow_teams = local.mlflow_teams
  mlflow_teams_passwords = module.mlflow.teams_passwords
  mlflow_teams_usernames = module.mlflow.teams_usernames
  mwaa_teams = local.mwaa_teams
  mwaa_teams_connections_prefixes = module.mwaa.teams_environment_connections_prefixes
  mwaa_teams_environment_names = module.mwaa.teams_environment_names
  mwaa_teams_variables_prefixes = module.mwaa.teams_environment_variables_prefixes
  rds_postgres_db_name                 = module.rds.postgres_db_name
  rds_postgres_host                    = module.rds.postgres_host
  rds_postgres_port                    = module.rds.postgres_port
  rds_postgres_teams = local.rds_postgres_teams
  rds_postgres_teams_passwords = module.postgres.teams_passwords
  rds_postgres_teams_usernames = module.postgres.teams_usernames
  s3_teams = local.s3_teams

  depends_on = [
    module.iam
  ]
}