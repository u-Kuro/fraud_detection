# IAM
# /teams
variable "iam_teams_names" { type = map(string) }

# MWAA
# /teams
variable "mwaa_teams" { type = set(string) }

# S3
# /teams
variable "s3_teams" { type = set(string) }

# SSM Parameter
# /teams
variable "ssm_teams_parameter_path" { type = map(string) }