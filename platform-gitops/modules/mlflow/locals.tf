# INPUTS
locals {
  aws    = var.aws
  mlflow = var.mlflow
  rds    = var.rds
  s3     = var.s3
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
  scripts = {
    files = {
      create_mlflow_workspace = {
        name = "create_mlflow_workspace.sh"
        relative = {
          path = "${local.scripts.relative.path}/${local.scripts.files.create_mlflow_workspace.name}"
        }
      }
    }
    relative = {
      path = "scripts"
    }
  }
}