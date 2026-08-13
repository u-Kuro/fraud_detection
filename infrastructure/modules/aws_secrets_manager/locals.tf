# INPUTS
locals {
  iam             = var.iam
  secrets_manager = var.secrets_manager
}
# COMPUTED
locals {
  # SECRETS MANAGER
  secrets_manager_arn = "arn:aws:secretsmanager:*:${local.iam.users.admin.account_id}:secret"
  secrets_manager_users = {
    teams = {
      for k, v in local.secrets_manager.users.teams : k => {
        path = k
      }
    }
  }
}