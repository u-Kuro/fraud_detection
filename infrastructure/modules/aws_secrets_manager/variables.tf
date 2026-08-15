# IAM
# /admin
variable "iam_admin_account_id" { type = string }
# /teams
variable "iam_teams_names" { type = map(string) }

# Secrets Manager
# /teams
variable "secrets_manager_teams" { type = set(string) }