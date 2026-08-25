locals {
  # SSM
  # /arns
  ssm_parameter_base_arn = "arn:aws:ssm:*:${var.iam_admin_account_id}:parameter"
  # /teams
  ssm_teams_parameter_paths = { for v in var.ssm_teams : v => v }
  ssm_teams_parameter_arns = {
    for k, v in local.ssm_teams_parameter_paths : k => "${local.ssm_parameter_base_arn}:${v}"
  }
}