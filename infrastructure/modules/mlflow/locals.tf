# TODO - 13/08/2026 - Continue here...
# INPUTS
locals {
  iam    = var.iam
  elb    = var.elb
  mlflow = var.mlflow
  rds    = var.rds
  s3     = var.s3
}
# COMPUTED
locals {
  # SYSTEM PORTS
  system_ports = {
    http  = 80
    https = 443
  }
  # KUBERNETES
  eks = {
    kubernetes = {
      mlflow = {
        namespace = "mlflow"
      }
    }
  }
  # MLFLOW
  mlflow_url = {
    internal = "http://${local.mlflow.host}"
    ingress = "http://${local.elb.alb.dns_name}/${local.mlflow.host}"
  }
  # SCRIPTS
  scripts_relative_path                             = "scripts"
  create_mlflow_workspace_script_file_name          = "create_mlflow_workspace.sh"
  create_mlflow_workspace_script_file_relative_path = "${local.scripts_relative_path}/${local.create_mlflow_workspace_script_file_name}"
}