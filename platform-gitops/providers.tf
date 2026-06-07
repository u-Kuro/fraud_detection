# All AWS calls redirected to the local MiniStack container.
provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
  region     = var.aws_region

  endpoints {
    eks  = "http://localhost:4566"
    rds  = "http://localhost:4566"
    s3   = "http://localhost:4566"
    ecr  = "http://localhost:4566"
    mwaa = "http://localhost:4566"
    iam  = "http://localhost:4566"
  }

  # MiniStack S3 requires path-style — virtual-hosted style
  # (bucket.localhost) does not resolve.
  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
}

# Both providers read the kubeconfig written by the EKS module's
# PowerShell script during Phase 1 apply (see §4).
provider "kubernetes" {
  config_path = "${path.root}/kubeconfig/k3s.yaml"
}

provider "helm" {
  kubernetes {
    config_path = "${path.root}/kubeconfig/k3s.yaml"
  }
}