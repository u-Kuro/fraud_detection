# IAM
# /admin
variable "iam_admin_account_id" { type = string }
# /teams
variable "iam_teams_names" { type = map(string) }

# SSM
# /teams
variable "ssm_teams" { type = set(string) }