locals {
  # Scripts
  # /path
  scripts_relative_path = "scripts"

  # Teams
  # /workspace-names
  mlflow_teams_workspace_names = { for v in var.mlflow_teams : v => v }
  # /credentials
  mlflow_teams_usernames = { for v in var.mlflow_teams : v => v }
  mlflow_teams_passwords = { for v in var.mlflow_teams : v => v }
}