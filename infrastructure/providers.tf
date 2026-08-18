provider "aws" {
  access_key = var.aws_admin_access_key
  secret_key = var.aws_admin_secret_key
  region     = var.aws_admin_region

  # Routes requests to local aws emulator (MiniStack container)
  endpoints {
    ec2            = "http://localhost:4566"
    ecr            = "http://localhost:4566"
    elbv2          = "http://localhost:4566"
    eks            = var.eks_host_endpoint_url
    iam            = "http://localhost:4566"
    mwaa           = "http://localhost:4566"
    rds            = "http://localhost:4566"
    s3             = var.s3_host_endpoint_url
    secretsmanager = var.secrets_manager_host_endpoint_url
    ssm            = "http://localhost:4566"
    sts            = "http://localhost:4566"
  }

  # Forces S3 URLs to use "http://localhost:4566/bucket-name" (path-style)
  # instead of "http://bucket-name.localhost:4566" which fails local DNS resolution
  s3_use_path_style = true
  # Prevents Terraform from validating dummy credentials against real AWS STS servers
  skip_credentials_validation = true
  # Prevents Terraform from querying the EC2 metadata IP (169.254.169.254) to avoid local timeouts
  skip_metadata_api_check = true
  # Prevents Terraform from calling STS GetCallerIdentity to lookup a real 12-digit AWS Account ID
  skip_requesting_account_id = true
}

provider "postgresql" {
  host             = module.rds.postgres_egress_host
  port             = module.rds.postgres_egress_port
  database         = module.rds.postgres_db_name
  username         = module.rds.postgres_admin_username
  password         = module.rds.postgres_admin_password
  sslmode          = "require"
  expected_version = "15"
}

provider "kubernetes" {
  config_path = local_sensitive_file.kubeconfig_host.filename
}
provider "helm" {
  kubernetes = {
    config_path = local_sensitive_file.kubeconfig_host.filename
  }
}