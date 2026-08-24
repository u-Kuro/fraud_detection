# Get Ministack configurations
data "external" "ministack_configuration" {
  program     = ["powershell", "-File", "${local.scripts_directory_path}/get-ministack-configuration.ps1"]
  working_dir = path.root
}
# Connect AWS with Ministack
provider "aws" {
  access_key = var.aws_admin_access_key
  secret_key = var.aws_admin_secret_key
  region     = var.aws_admin_region

  # Routes requests to local aws emulator (MiniStack container)
  endpoints {
    ec2            = local.ministack_host_url
    ecr            = local.ministack_host_url
    elbv2          = local.ministack_host_url
    eks            = local.ministack_host_url
    iam            = local.ministack_host_url
    mwaa           = local.ministack_host_url
    rds            = local.ministack_host_url
    s3             = local.ministack_host_url
    secretsmanager = local.ministack_host_url
    ssm            = local.ministack_host_url
    sts            = local.ministack_host_url
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
# Set default AWS configurations for local script executions
resource "terraform_data" "configure_aws" {
  provisioner "local-exec" {
    interpreter = ["powershell", "-File"]
    command     = "${local.scripts_directory_path}/configure-aws.ps1"
    environment = {
      AWS_ACCESS_KEY_ID     = var.aws_admin_access_key
      AWS_SECRET_ACCESS_KEY = var.aws_admin_secret_key
      AWS_DEFAULT_REGION    = var.aws_admin_region
      AWS_ENDPOINT_URL      = local.ministack_host_url
    }
  }
}
# Get ECR authorization token mocked by Ministack
data "aws_ecr_authorization_token" "main" {}
# Connect to Postgres spawned by RDS from Ministack
provider "postgresql" {
  host             = module.rds.postgres_local_host
  port             = module.rds.postgres_local_port
  database         = module.rds.postgres_db_name
  username         = module.rds.postgres_admin_username
  password         = module.rds.postgres_admin_password
  expected_version = module.rds.postgres_version
}
# Connect to K3s spawned by EKS from Ministack
provider "kubernetes" {
  config_path = local_sensitive_file.kubeconfig_for_localhost.filename
}
provider "helm" {
  kubernetes = {
    config_path = local_sensitive_file.kubeconfig_for_localhost.filename
  }
}