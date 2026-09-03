# Connect AWS with MiniStack
provider "aws" {
  access_key               = var.aws_admin_access_key
  secret_key               = var.aws_admin_secret_key
  region                   = var.aws_admin_region
  shared_config_files      = []
  shared_credentials_files = []

  # Routes requests to local aws emulator (MiniStack container)
  endpoints {
    ec2            = module.ministack_container.host_url
    ecr            = module.ministack_container.host_url
    elbv2          = module.ministack_container.host_url
    eks            = module.ministack_container.host_url
    iam            = module.ministack_container.host_url
    mwaa           = module.ministack_container.host_url
    rds            = module.ministack_container.host_url
    s3             = module.ministack_container.host_url
    secretsmanager = module.ministack_container.host_url
    ssm            = module.ministack_container.host_url
    sts            = module.ministack_container.host_url
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
resource "terraform_data" "configure_local_aws" {
  provisioner "local-exec" {
    interpreter = ["pwsh", "-File"]
    command     = "${local.scripts_directory_path}/configure-aws.ps1"
    environment = {
      AWS_ACCESS_KEY_ID     = var.aws_admin_access_key
      AWS_SECRET_ACCESS_KEY = var.aws_admin_secret_key
      AWS_DEFAULT_REGION    = var.aws_admin_region
      AWS_ENDPOINT_URL      = module.ministack_container.host_url
    }
  }
  depends_on = [
    module.main_docker_network,
    module.ministack_container,
  ]
}
# Get ECR authorization token mocked by MiniStack
data "aws_ecr_authorization_token" "main" {}
# Connect to Postgres spawned by RDS from MiniStack
provider "postgresql" {
  host             = module.rds.postgres_local_host
  port             = module.rds.postgres_local_port
  database         = module.rds.postgres_db_name
  username         = module.rds.postgres_admin_username
  password         = module.rds.postgres_admin_password
  expected_version = module.rds.postgres_version
  sslmode          = "disable"
  max_connections  = 1
}
# Connect to K3s spawned by EKS from MiniStack
provider "kubernetes" {
  config_path = local_sensitive_file.kubeconfig_for_localhost.filename
}
provider "kubectl" {
  config_path      = local_sensitive_file.kubeconfig_for_localhost.filename
  load_config_file = true
}
provider "helm" {
  plugins_path           = "${local.helm_directory_path}/plugins"
  registry_config_path   = "${local.helm_directory_path}/registry.json"
  repository_config_path = "${local.helm_directory_path}/repositories.yaml"
  repository_cache       = "${local.helm_directory_path}/cache"
  kubernetes = {
    config_path = local_sensitive_file.kubeconfig_for_localhost.filename
  }
}