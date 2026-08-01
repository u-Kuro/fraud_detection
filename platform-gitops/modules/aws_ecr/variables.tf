variable "aws_account_id" { type = string }

# From aws_iam module output: map of team_key => IAM Role ARN
variable "team_role_arns" {
  type = map(string)
}

# From aws_iam module output: map of team_key => IAM Role name (for policy attachment)
variable "team_role_names" {
  type = map(string)
}