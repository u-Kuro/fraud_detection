# ── Teams (defined once, threaded through all modules) ────────────────────────
locals {
  teams = {
    # TODO - Need to remove mlflow here since its not a team. e.g. it created a migration in postgresql
    mlflow = {
      namespace               = "mlflow"
      ecr_repos               = []
      has_mwaa_access         = false
      has_mlflow_access       = true
      mlflow_workspace        = "mlflow-workspace"
      pg_schema               = "mlflow"
      pg_username             = var.mlflow_postgresql_username
      pg_password             = var.mlflow_postgresql_password
      pg_migrations_username  = null
      pg_migrations_password  = null
      s3_team_bucket          = null
      s3_bucket               = null
      shared_s3_paths         = []
      shared_configmap_access = false
    }
    mle = {
      namespace               = "mle"
      ecr_repos               = ["archive", "drift_check", "fraud_detection", "train_model"]
      has_mwaa_access         = true
      has_mlflow_access       = true
      mlflow_workspace        = "mle-workspace"
      pg_schema               = "mle"
      pg_username             = var.mle_postgresql_username
      pg_password             = var.mle_postgresql_password
      pg_migrations_username  = var.mle_migrations_postgresql_username
      pg_migrations_password  = var.mle_migrations_postgresql_password
      s3_team_bucket          = "mle"
      s3_bucket               = "mle"
      shared_s3_paths         = ["airflow/connections/mle", "airflow/variables/mle"]
      shared_configmap_access = true
    }
  }
}

module "ecr_repository" {
  source         = "./modules/aws_ecr"
  teams          = local.teams
  team_role_arns = module.aws_iam_oidc.team_role_arns
}

# Creates local EKS container from local AWS emulator (MiniStack)
# then Copies its k3s.yaml (kubeconfig)
# into Other local emulated services (e.g. MWAA)
# to Allow access to manage cluster resources
module "eks_cluster" {
  source = "./modules/aws_eks"

  aws_account_id                   = var.aws_account_id
  aws_access_key                   = var.aws_access_key
  aws_secret_key                   = var.aws_secret_key
  aws_region                       = var.aws_region
  eks_service_endpoint_url         = var.eks_service_endpoint_url
  kubeconfig_host_directory_path   = var.kubeconfig_host_directory_path
  kubeconfig_host_file_name        = var.kubeconfig_host_file_name
  ecr_registry_endpoint            = var.ecr_registry_endpoint
  ecr_registry_mirror_endpoint_url = var.ecr_registry_mirror_endpoint_url
  ecr_registry_mirror_endpoint     = var.ecr_registry_mirror_endpoint
  ecr_registry_secret_name         = var.ecr_registry_secret_name

  teams          = local.teams
  team_role_arns = module.aws_iam_oidc.team_role_arns
}

module "rds_db" {
  source      = "./modules/aws_rds"
  db_username = var.rds_db_username
  db_password = var.rds_db_password
}

module "s3" {
  source = "./modules/aws_s3"
  teams  = local.teams
}

module "secrets_manager" {
  source         = "./modules/aws_secrets_manager"
  aws_account_id = var.aws_account_id
  aws_region     = var.aws_region
  teams          = local.teams
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

  eks_service_endpoint_url = var.eks_service_endpoint_url
  eks_cluster_name         = module.eks_cluster.name

  s3_service_endpoint_url = var.s3_service_endpoint_url
  s3_mwaa_bucket           = module.s3.mwaa_bucket_name

  aws_account_id = var.aws_account_id

  secretsmanager_service_endpoint_url = var.secretsmanager_service_endpoint_url

  teams = local.teams

  depends_on = [module.eks_cluster, module.s3]
}

module "postgresql" {
  source            = "./modules/postgresql"
  db_name           = module.rds_db.name
  db_owner_username = module.rds_db.username
  teams             = local.teams
  depends_on        = [module.rds_db]
}

module "helm_apps" {
  source = "./modules/helm_apps"

  rds_db_address             = module.rds_db.address
  rds_db_port                = module.rds_db.port
  rds_db_name                = module.rds_db.name
  s3_internal_endpoint_url   = var.s3_internal_endpoint_url
  s3_mlflow_bucket_aws_region = module.s3.mlflow_bucket_aws_region
  s3_mlflow_bucket           = module.s3.mlflow_bucket_name
  mlflow_db_username         = module.postgresql.team_usernames["mlflow"]
  mlflow_db_password         = module.postgresql.team_passwords["mlflow"]
  aws_access_key             = var.aws_access_key
  aws_secret_key             = var.aws_secret_key
  teams                      = local.teams

  depends_on = [module.eks_cluster, module.rds_db, module.s3, module.postgresql]
}

# ── NEW: OIDC + IRSA (depends on EKS cluster OIDC issuer URL) ────────────────
module "aws_iam_oidc" {
  source = "./modules/aws_iam_oidc"

  aws_account_id      = var.aws_account_id
  aws_region          = var.aws_region
  eks_oidc_issuer_url = module.eks_cluster.oidc_issuer_url
  shared_s3_bucket    = module.s3.mwaa_bucket_name
  teams = {
    for k, v in local.teams : k => {
      namespace        = v.namespace
      ecr_repos        = v.ecr_repos
      has_mwaa_access  = v.has_mwaa_access
      s3_team_bucket   = v.s3_team_bucket
      shared_s3_paths  = v.shared_s3_paths
    }
  }
  depends_on = [module.eks_cluster]
}

# ── NEW: Kubernetes Namespaces, RBAC, ConfigMaps, Secrets ────────────────────
module "kubernetes_resources" {
  source = "./modules/kubernetes_resources"

  team_role_arns      = module.aws_iam_oidc.team_role_arns
  rds_host            = module.rds_db.address
  rds_port            = module.rds_db.port
  rds_db_name         = module.rds_db.name
  aws_region          = var.aws_region
  s3_endpoint_url     = var.s3_internal_endpoint_url
  mlflow_tracking_uri = module.helm_apps.mlflow_tracking_uri
  mwaa_webserver_url  = module.aws_mwaa_environment.webserver_url

  teams = {
    for k, v in local.teams : k => {
      namespace               = v.namespace
      shared_configmap_access = v.shared_configmap_access
      pg_schema               = v.pg_schema
      pg_username             = v.pg_username
      pg_password             = v.pg_password
      s3_bucket               = v.s3_bucket
      mlflow_workspace        = v.mlflow_workspace
      has_mwaa_access         = v.has_mwaa_access
    }
  }

  depends_on = [
    module.aws_iam_oidc,
    module.eks_cluster,
    module.rds_db,
    module.helm_apps,
    module.aws_mwaa_environment,
  ]
}