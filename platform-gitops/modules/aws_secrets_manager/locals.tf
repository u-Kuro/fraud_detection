# INPUTS
locals {
  aws = var.aws
}
# COMPUTED
locals {
  # SECRETS MANAGER
  secretsmanager = {
    arn = "arn:aws:secretsmanager:*:${local.aws.users.admin.account_id}:secret"
  }
}