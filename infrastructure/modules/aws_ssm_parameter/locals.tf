# INPUTS
locals {
  iam           = var.iam
  ssm_parameter = var.ssm_parameter
}
# COMPUTED
locals {
  # SSM PARAMETER
  ssm_parameter_arn = "arn:aws:ssm:*:${local.iam.users.admin.account_id}:parameter"
  ssm_parameter_users = {
    teams = {
      for k, v in local.ssm_parameter.users.teams : k => {
        path = k
      }
    }
  }
}