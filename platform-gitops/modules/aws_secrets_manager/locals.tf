# INPUTS
locals {
  iam             = var.iam
  secrets_manager = var.secrets_manager
}
# COMPUTED
locals {
  # SECRETS MANAGER
  secrets_manager_arn = "arn:aws:secretsmanager:*:${local.iam.users.admin.account_id}:secret"
}