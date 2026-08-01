# From aws_iam module: map of team_key => IAM Role name
variable "team_role_names" {
  type    = map(string)
  default = {}
}