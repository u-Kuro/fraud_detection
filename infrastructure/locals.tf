locals {
  # ECR
  # /authorization
  ecr_username            = data.aws_ecr_authorization_token.main.user_name
  ecr_password            = data.aws_ecr_authorization_token.main.password
  ecr_authorization_token = data.aws_ecr_authorization_token.main.authorization_token
  # /urls
  ecr_url          = module.ministack_container.url
  ecr_endpoint     = module.ministack_container.endpoint
  ecr_aws_url      = data.aws_ecr_authorization_token.main.proxy_endpoint
  ecr_aws_endpoint = replace(local.ecr_aws_url, "/^[^:]+:\\/\\//", "")

  # EKS
  # /domains
  eks_ingress_domain           = "${module.eks.container_ip}.${var.sslip_io_public_wildcard_dns_domain}"
  eks_ingress_domain_from_host = "127.0.0.1.${var.sslip_io_public_wildcard_dns_domain}"
  # /teams
  eks_teams_namespaces = { for v in local.eks_teams : v => v }

  # Local files
  # /paths
  local_files_directory_path         = "${path.root}/local_files"
  helm_directory_path                = "${path.root}/.helm"
  kubeconfig_for_localhost_file_path = "${local.local_files_directory_path}/kubeconfig_for_localhost.yaml"
  kubeconfig_file_path               = "${local.local_files_directory_path}/kubeconfig.yaml"

  # MWAA
  # /urls
  mwaa_url = module.ministack_container.url

  # S3
  # /urls
  s3_url = module.ministack_container.url

  # Secrets Manager
  # /urls
  secrets_manager_url = module.ministack_container.url

  # Scripts
  # /paths
  scripts_directory_path = "${path.root}/scripts"

  # Teams
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
        postgres        = true
      }
    }
  }
  iam_teams             = keys(local.teams)
  ecr_teams             = [for key, team in local.teams : key if team.includes.ecr]
  eks_teams             = [for key, team in local.teams : key if team.includes.eks]
  mlflow_teams          = [for key, team in local.teams : key if team.includes.mlflow]
  mwaa_teams            = [for key, team in local.teams : key if team.includes.mwaa]
  postgres_teams        = [for key, team in local.teams : key if team.includes.postgres]
  s3_teams              = [for key, team in local.teams : key if team.includes.s3]
  secrets_manager_teams = [for key, team in local.teams : key if team.includes.secrets_manager]
  ssm_teams             = [for key, team in local.teams : key if team.includes.ssm]
}

# Create registries file to redirect container registry calls to MiniStack's ECR
resource "local_sensitive_file" "eks_registries" {
  filename        = "${local.local_files_directory_path}/registries.yaml"
  file_permission = "0600"
  content = yamlencode({
    mirrors = {
      (local.ecr_aws_endpoint) = {
        endpoint = [local.ecr_url]
      }
    }
    configs = {
      (local.ecr_endpoint) = {
        auth = {
          username = local.ecr_username
          password = local.ecr_password
        }
      }
    }
  })
}
# Initialize kubeconfig file to access K8s cluster locally
resource "local_sensitive_file" "kubeconfig_for_localhost" {
  filename        = local.kubeconfig_for_localhost_file_path
  file_permission = "0600"
  content         = fileexists(local.kubeconfig_for_localhost_file_path) ? sensitive(file(local.kubeconfig_for_localhost_file_path)) : ""
}
# Initialize kubeconfig file to access K8s cluster in docker network
resource "local_sensitive_file" "kubeconfig_for_docker" {
  filename        = local.kubeconfig_file_path
  file_permission = "0600"
  content         = fileexists(local.kubeconfig_file_path) ? sensitive(file(local.kubeconfig_file_path)) : ""
}
# Initialize MWAA python package requirements
resource "local_sensitive_file" "mwaa_requirements" {
  filename        = "${local.local_files_directory_path}/requirements.txt"
  file_permission = "0600"
  content         = <<-EOT
    apache-airflow==3.3.1
    apache-airflow-providers-amazon==9.34.0
    apache-airflow-providers-cncf-kubernetes==10.21.0
    apache-airflow-providers-http==6.0.5
    apache-airflow-providers-postgres==7.0.1
    apache-airflow-providers-slack==9.10.2
    mlflow-skinny==3.15.2
    pydantic==2.13.4
    pydantic-settings==2.15.0
  EOT
}