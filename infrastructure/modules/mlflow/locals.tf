# COMPUTED
locals {
  # Scripts
  # /file-name
  create_mlflow_workspace_script_file_name          = "create_mlflow_workspace.sh"
  # /path
  scripts_relative_path                             = "scripts"
  create_mlflow_workspace_script_file_relative_path = "${local.scripts_relative_path}/${local.create_mlflow_workspace_script_file_name}"
}