locals {
  # SSM
  # /arns
  ssm_parameter_base_arn = "arn:aws:ssm:*:${var.iam_admin_account_id}:parameter"
  # /teams
  ssm_teams_parameter_paths = { for v in var.ssm_teams : v => v }
}