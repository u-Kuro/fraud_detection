# TODO - 25/08/2026 - Continue here... Try running?
module "iam" {
  source = "./modules/aws/iam"

  # IAM
  # /teams
  iam_teams = local.iam_teams
}

module "ecr" {
  source = "./modules/aws/ecr"

  # IAM
  # /admin
  iam_admin_account_id = module.iam.admin_account_id
  iam_teams_names      = module.iam.teams_names

  # ECR
  # /teams
  ecr_teams = local.ecr_teams

  depends_on = [
    module.iam
  ]
}

module "secrets_manager" {
  source = "./modules/aws/secrets_manager"

  # IAM
  # /admin
  iam_admin_account_id = module.iam.admin_account_id
  # /teams
  iam_teams_names = module.iam.teams_names

  # Secrets Manager
  # /teams
  secrets_manager_teams = local.secrets_manager_teams

  depends_on = [
    module.iam
  ]
}

module "ssm" {
  source = "./modules/aws/ssm"

  # IAM
  # /admin
  iam_admin_account_id = module.iam.admin_account_id
  # /teams
  iam_teams_names = module.iam.teams_names

  # SSM
  # /teams
  ssm_teams = local.ssm_teams

  depends_on = [
    module.iam
  ]
}

module "s3" {
  source = "./modules/aws/s3"

  # IAM
  # /teams
  iam_teams_names = module.iam.teams_names

  # MWAA
  # /teams
  mwaa_teams = local.mwaa_teams

  # S3
  # /teams
  s3_teams = local.s3_teams

  # SSM
  # /teams
  ssm_teams_parameter_paths = module.ssm.teams_parameter_paths

  depends_on = [
    module.iam,
    module.ssm,
  ]
}

module "rds" {
  source = "./modules/aws/rds"

  # IAM
  # /services
  iam_rds_role_name = module.iam.rds_role_name

  # Ministack
  # /network
  ministack_network_name = local.ministack_network_name

  # RDS
  # /postgres
  rds_postgres_admin_username = var.rds_postgres_admin_username
  rds_postgres_admin_password = var.rds_postgres_admin_password
  # /teams
  postgres_teams = local.postgres_teams

  # S3
  # /postgres
  s3_postgres_bucket_arn = module.s3.postgres_bucket_arn

  # SSM
  # /teams
  ssm_teams_parameter_paths = module.ssm.teams_parameter_paths

  depends_on = [
    module.iam,
    module.s3,
    module.ssm,
  ]
}

module "postgres" {
  source = "./modules/postgres"

  # RDS
  # /postgres
  rds_postgres_local_host     = module.rds.postgres_local_host
  rds_postgres_local_port     = module.rds.postgres_local_port
  rds_postgres_admin_username = module.rds.postgres_admin_username
  rds_postgres_db_name        = module.rds.postgres_db_name
  # /mlflow-schema
  rds_postgres_mlflow_username = var.rds_postgres_mlflow_username
  rds_postgres_mlflow_password = var.rds_postgres_mlflow_password
  # /teams
  rds_postgres_teams = local.postgres_teams

  # Secrets Manager
  # /teams
  secrets_manager_teams_secret_paths = module.secrets_manager.teams_secret_paths

  # SSM
  # /teams
  ssm_teams_parameter_paths = module.ssm.teams_parameter_paths

  depends_on = [
    module.rds,
    module.secrets_manager,
    module.ssm,
  ]
}

module "eks" {
  source = "./modules/aws/eks"

  # IAM
  # /admin
  iam_admin_arn = module.iam.admin_arn
  # /teams
  iam_teams_arns = module.iam.teams_arns
  # /services
  iam_ec2_role_arn  = module.iam.ec2_role_arn
  iam_ec2_role_name = module.iam.ec2_role_name
  iam_eks_role_arn  = module.iam.eks_role_arn
  iam_eks_role_name = module.iam.eks_role_name

  # EKS
  # /teams
  eks_teams            = local.eks_teams
  eks_teams_namespaces = local.eks_teams_namespaces

  # Local Files
  # /paths
  local_files_kubeconfig_for_localhost_file_path = local_sensitive_file.kubeconfig_for_localhost.filename
  local_files_kubeconfig_for_docker_file_path    = local_sensitive_file.kubeconfig_for_docker.filename
  local_files_eks_registries_file_path           = local_sensitive_file.eks_registries.filename

  # Ministack
  # /network
  ministack_network_name    = local.ministack_network_name
  ministack_network_gateway = local.ministack_network_gateway

  # Secrets Manager
  # /teams
  ssm_teams_parameter_paths = module.ssm.teams_parameter_paths

  # SSM
  # /teams
  secrets_manager_teams_secret_paths = module.secrets_manager.teams_secret_paths

  depends_on = [
    module.iam,
    local_sensitive_file.kubeconfig_for_localhost,
    local_sensitive_file.kubeconfig_for_docker,
    local_sensitive_file.eks_registries,
    module.ssm,
    module.secrets_manager,
  ]
}

module "kyverno" {
  source = "./modules/k8s/kyverno"

  depends_on = [
    module.eks,
  ]
}

module "metallb" {
  source = "./modules/k8s/metallb"

  eks_container_ip = module.eks.container_ip

  depends_on = [
    module.eks,
  ]
}

module "traefik" {
  source = "./modules/k8s/traefik"

  # EKS
  # /urls
  eks_container_host_port = module.eks.container_host_port

  # MetalLB
  # /ip
  metallb_eks_ip = module.metallb.eks_ip
  # /resources
  metallb_eks_ip_address_pool_name = module.metallb.eks_ip_address_pool_name

  depends_on = [
    module.eks,
    module.metallb
  ]
}

module "mwaa" {
  source = "./modules/aws/mwaa"

  # IAM
  # /admin
  iam_admin_account_id = module.iam.admin_account_id
  iam_admin_region     = module.iam.admin_region
  # /teams
  iam_teams_names     = module.iam.teams_names
  iam_teams_arns      = module.iam.teams_arns
  iam_teams_usernames = module.iam.teams_usernames
  iam_teams_passwords = module.iam.teams_passwords

  # Local Files
  # /paths
  local_files_kubeconfig_for_docker_file_path = module.eks.local_files_kubeconfig_for_docker_file_path
  local_files_mwaa_requirements_file_path     = local_sensitive_file.mwaa_requirements.filename
  # /content
  local_files_kubeconfig_for_docker_file_md5 = local_sensitive_file.kubeconfig_for_docker.content_md5
  local_files_mwaa_requirements_file_md5     = local_sensitive_file.mwaa_requirements.content_md5

  # Ministack
  # /container
  ministack_network_name = local.ministack_network_name
  # /urls
  ministack_container_ip   = local.ministack_container_ip
  ministack_container_port = local.ministack_container_port

  # MWAA
  # /teams
  mwaa_teams = local.mwaa_teams

  # S3
  # /mwaa
  s3_teams_mwaa_bucket_names = module.s3.teams_mwaa_bucket_names
  s3_teams_mwaa_bucket_arns  = module.s3.teams_mwaa_bucket_arns

  # Secrets Manager
  # /urls
  secrets_manager_url = local.secrets_manager_url

  # SSM
  # /teams
  ssm_teams_parameter_paths = module.ssm.teams_parameter_paths

  depends_on = [
    module.iam,
    module.eks,
    local_sensitive_file.mwaa_requirements,
    module.s3,
    module.ssm,
  ]
}

module "mlflow" {
  source = "./modules/k8s/mlflow"

  # IAM
  # /admin
  iam_admin_access_key = var.aws_admin_access_key
  iam_admin_secret_key = var.aws_admin_secret_key
  iam_admin_region     = module.iam.admin_region

  # EKS
  # /domain
  eks_ingress_domain           = local.eks_ingress_domain
  eks_ingress_domain_from_host = local.eks_ingress_domain_from_host

  # MLflow
  # /deployment
  mlflow_flask_server_secret_key = var.mlflow_flask_server_secret_key
  mlflow_admin_username          = var.mlflow_admin_username
  mlflow_admin_password          = var.mlflow_admin_password
  # /teams
  mlflow_teams = local.mlflow_teams

  # RDS
  # /postgres
  rds_postgres_db_name = module.rds.postgres_db_name
  rds_postgres_host    = module.rds.postgres_host
  rds_postgres_port    = module.rds.postgres_port
  # /mlflow-schema
  rds_postgres_mlflow_username = var.rds_postgres_mlflow_username
  rds_postgres_mlflow_password = var.rds_postgres_mlflow_password

  # S3
  # /urls
  s3_url                = local.s3_url
  s3_mlflow_bucket_name = module.s3.mlflow_bucket_name

  # Secrets Manager
  # /teams
  secrets_manager_teams_secret_paths = module.secrets_manager.teams_secret_paths

  # SSM
  # /teams
  ssm_teams_parameter_paths = module.ssm.teams_parameter_paths

  # Traefik
  # /entry-points
  traefik_eks_host_entry_point_name = module.traefik.eks_host_entry_point_name
  # /ports
  traefik_eks_host_port = module.traefik.eks_host_port

  depends_on = [
    module.iam,
    module.postgres,
    module.rds,
    module.s3,
    module.secrets_manager,
    module.ssm,
    module.traefik,
  ]
}

module "exports" {
  source = "./modules/exports"

  # IAM
  # /admin
  iam_admin_region = module.iam.admin_region
  # /teams
  iam_teams_usernames = module.iam.teams_usernames
  iam_teams_passwords = module.iam.teams_passwords

  # ECR
  # /aws
  ecr_aws_endpoint                     = local.ecr_aws_endpoint
  ecr_aws_authorization_token          = local.ecr_authorization_token
  ecr_aws_authorization_token_username = local.ecr_username
  ecr_aws_authorization_token_password = local.ecr_password

  # EKS
  # /teams
  eks_teams            = local.eks_teams
  eks_teams_namespaces = local.eks_teams_namespaces

  # MLflow
  # /urls
  mlflow_ingress_url = module.mlflow.ingress_url
  mlflow_inter_url   = module.mlflow.inter_url
  # /teams
  mlflow_teams           = local.mlflow_teams
  mlflow_teams_usernames = module.mlflow.teams_usernames
  mlflow_teams_passwords = module.mlflow.teams_passwords

  # MWAA
  # /urls
  mwaa_url = local.mwaa_url
  # /teams
  mwaa_teams                       = local.mwaa_teams
  mwaa_teams_environment_names     = module.mwaa.teams_environment_names
  mwaa_teams_connections_prefixes  = module.mwaa.teams_environment_connections_prefixes
  mwaa_teams_variables_prefixes    = module.mwaa.teams_environment_variables_prefixes
  mwaa_teams_kubeconfig_file_paths = module.mwaa.teams_environment_kubeconfig_file_paths

  # RDS
  # /postgres
  rds_postgres_host    = module.rds.postgres_host
  rds_postgres_port    = module.rds.postgres_port
  rds_postgres_db_name = module.rds.postgres_db_name
  # /teams
  rds_postgres_teams           = local.postgres_teams
  rds_postgres_teams_usernames = module.postgres.teams_usernames
  rds_postgres_teams_passwords = module.postgres.teams_passwords

  # S3
  # /urls
  s3_url = local.s3_url
  # /teams
  s3_teams              = local.s3_teams
  s3_teams_bucket_names = module.s3.teams_bucket_names

  depends_on = [
    module.iam,
    module.eks,
    module.kyverno,
    module.mlflow,
    module.mwaa,
    module.rds,
    module.postgres,
    module.s3,
  ]
}