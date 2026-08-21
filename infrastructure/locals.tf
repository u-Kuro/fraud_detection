locals {
  # ECR
  # /authorization
  ecr_username            = data.aws_ecr_authorization_token.main.user_name
  ecr_password            = data.aws_ecr_authorization_token.main.password
  ecr_authorization_token = data.aws_ecr_authorization_token.main.authorization_token
  # /urls
  ecr_url = local.ministack_url
  ecr_endpoint = local.ministack_endpoint
  ecr_aws_url = data.aws_ecr_authorization_token.main.proxy_endpoint
  ecr_aws_endpoint = replace(local.ecr_aws_url, "/^[^:]+:\\/\\//", "")

  # EKS
  # /urls
  eks_host_url = local.ministack_host_url
  # /domain
  eks_ingress_domain = "${module.eks.container_ip}.${var.sslip_io_public_wildcard_dns_domain}"
  eks_ingress_domain_from_host = "127.0.0.1.${var.sslip_io_public_wildcard_dns_domain}"

  # Local files
  # /path
  local_files_directory_path             = "${path.root}/local_files"

  # Ministack
  # /network
  ministack_network_name        = data.external.ministack_configuration.result.ministack_network_name
  ministack_network_gateway     = data.external.ministack_configuration.result.ministack_network_gateway
  # /container
  ministack_container_name      = data.external.ministack_configuration.result.ministack_container_name
  ministack_container_ip        = data.external.ministack_configuration.result.ministack_container_ip
  ministack_container_host_port = data.external.ministack_configuration.result.ministack_container_host_port
  # /urls
  ministack_host_url            = data.external.ministack_configuration.result.ministack_host_url
  ministack_url                 = data.external.ministack_configuration.result.ministack_url
  ministack_endpoint            = data.external.ministack_configuration.result.ministack_endpoint

  # Secrets Manager
  # /urls
  secrets_manager_url           = local.ministack_url

  # Scripts
  # /paths
  scripts_directory_path                 = "${path.root}/scripts"

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
  ecr_teams             = [for key, team in local.teams : key if team.includes.ecr]
  eks_teams             = [for key, team in local.teams : key if team.includes.eks]
  mlflow_teams          = [for key, team in local.teams : key if team.includes.mlflow]
  mwaa_teams            = [for key, team in local.teams : key if team.includes.mwaa]
  rds_postgres_teams    = [for key, team in local.teams : key if team.includes.postgres]
  s3_teams              = [for key, team in local.teams : key if team.includes.s3]
  secrets_manager_teams = [for key, team in local.teams : key if team.includes.secrets_manager]
  ssm_teams             = [for key, team in local.teams : key if team.includes.ssm]
}

# Initialize kubeconfig file to access K8s cluster locally
resource "local_sensitive_file" "kubeconfig_for_localhost" {
  filename        = "${local.local_files_directory_path}/kubeconfig_for_localhost.yaml"
  file_permission = "0600"
}
# Initialize kubeconfig file to access K8s cluster in docker network
resource "local_sensitive_file" "kubeconfig_for_docker" {
  filename        = "${local.local_files_directory_path}/kubeconfig.yaml"
  file_permission = "0600"
}
# Create registries file to redirect container registry calls to Ministack's ECR
resource "local_sensitive_file" "registries" {
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
# Initialize MWAA python package requirements
resource "local_sensitive_file" "mwaa_requirements" {
  filename        = "${local.local_files_directory_path}/requirements.txt"
  file_permission = "0600"
  content = <<-EOT
    apache-airflow==3.0.6
    apache-airflow-providers-amazon==9.12.0
    apache-airflow-providers-cncf-kubernetes==10.7.0
    apache-airflow-providers-http==5.3.3
    apache-airflow-providers-postgres==6.2.3
    apache-airflow-providers-slack==9.1.4
    pydantic==2.11.7
    pydantic-settings==2.15.0
  EOT
}