# INPUTS
locals {
  aws = var.aws
  mlflow = var.mlflow
  rds = var.rds
  s3 = var.s3
}
# COMPUTED
locals {
  # KUBERNETES
  eks = {
    kubernetes = {
      mlflow = {
        namespace = "mlflow"
      }
    }
  }
  # MLFLOW
  mlflow_tracking_uri = "http://${local.mlflow.host}:${local.mlflow.port}"
  # SCRIPTS
  scripts_path_name = "scripts"
  create_mflow_workspace_script_file_name = "create_mlflow_workspace.sh"
}