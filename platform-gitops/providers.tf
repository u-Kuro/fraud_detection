provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region     = var.aws_region

  # Routes requests to local aws emulator (MiniStack container)
  endpoints {
    eks             = var.eks_service_endpoint_url
    s3              = var.s3_service_endpoint_url
    ecr             = "http://localhost:4566"
    mwaa            = "http://localhost:4566"
    rds             = "http://localhost:4566"
    secretsmanager  = var.secretsmanager_service_endpoint_url
    iam             = "http://localhost:4566"
  }

  # Forces S3 URLs to use "http://localhost:4566/bucket-name" (path-style)
  # instead of "http://bucket-name.localhost:4566" which fails local DNS resolution
  s3_use_path_style           = true
  # Prevents Terraform from validating dummy credentials against real AWS STS servers
  skip_credentials_validation = true
  # Prevents Terraform from querying the EC2 metadata IP (169.254.169.254) to avoid local timeouts
  skip_metadata_api_check     = true
  # Prevents Terraform from calling STS GetCallerIdentity to lookup a real 12-digit AWS Account ID
  skip_requesting_account_id  = true
}

provider "postgresql" {
  host              = module.rds_db.address
  port              = module.rds_db.port
  database          = module.rds_db.name
  username          = module.rds_db.username
  password          = module.rds_db.password
  sslmode           = "require"
  expected_version  = "15"
}

locals {
  kubeconfig_file_path = "${var.kubeconfig_host_directory_path}/${var.kubeconfig_host_file_name}"
}
provider "kubernetes" {
  config_path = local.kubeconfig_file_path
}
provider "helm" {
  kubernetes = {
    config_path = local.kubeconfig_file_path
  }
}