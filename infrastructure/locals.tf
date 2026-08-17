locals {
  ecr_teams = [for key, team in local.teams : key if team.includes.ecr]
  eks_teams = [for key, team in local.teams : key if team.includes.eks]
  mlflow_teams = [for key, team in local.teams : key if team.includes.mlflow]
  mwaa_teams = [for key, team in local.teams : key if team.includes.mwaa]
  rds_postgres_teams = [for key, team in local.teams : key if team.includes.postgres]
  s3_teams = [for key, team in local.teams : key if team.includes.s3]
  secrets_manager_teams = [for key, team in local.teams : key if team.includes.secrets_manager]
  ssm_teams = [for key, team in local.teams : key if team.includes.ssm]
}

resource "local_sensitive_file" "kubeconfig_host" {
  filename        = "${local.local_files_directory_path}/kubeconfig_host.yaml"
  file_permission = "0600"
}
resource "local_sensitive_file" "mwaa_requirements" {
  filename        = "${local.local_files_directory_path}/requirements.txt"
  file_permission = "0600"
}