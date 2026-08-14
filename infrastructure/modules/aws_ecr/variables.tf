# IAM
# /admin
variable "iam_admin_account_id" { type = string }
# /teams
variable "iam_teams_role_name" { type = map(string) }

# ECR
# /teams
variable "ecr_teams" { type = set(string) }