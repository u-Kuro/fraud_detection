locals {
  # Scripts
  # /files
  create_mlflow_workspace_script_file_name = "create-mlflow-workspace.sh"
  # /paths
  scripts_relative_path                             = "scripts"
  create_mlflow_workspace_script_file_relative_path = "${local.scripts_relative_path}/${local.create_mlflow_workspace_script_file_name}"

  # EKS
  # /jobs
  create_mlflow_workspace_script_file_resource_name = "create-mlflow-workspace-script"

  # MLflow
  # /hosts
  mlflow_inter_host = "${var.mlflow_host}.${var.eks_mlflow_namespace}.svc.cluster.local"
  # /domains
  mlflow_subdomain           = "${var.mlflow_host}.${var.eks_ingress_domain}"
  mlflow_subdomain_from_host = "${var.mlflow_host}.${var.eks_ingress_domain_from_host}"
  # /urls
  mlflow_intra_url   = "http://${var.mlflow_host}"
  mlflow_inter_url   = "http://${local.mlflow_inter_host}"
  mlflow_ingress_url = "http://${local.mlflow_subdomain}"
  mlflow_host_url    = "http://${local.mlflow_subdomain_from_host}"

  # Teams
  # /mlflow-roles
  mlflow_teams_role_names = { for v in var.mlflow_teams : v => v }
  # /workspace-names
  mlflow_teams_workspace_names = { for v in var.mlflow_teams : v => v }
  # /credentials
  mlflow_teams_usernames = { for v in var.mlflow_teams : v => "${v}-0123456789" }
  mlflow_teams_passwords = { for v in var.mlflow_teams : v => "${v}-0123456789" }
}