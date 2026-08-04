variable "teams" {
  type = map(object({
    ecr_repositories = set(string)
    role_arn         = string
  }))
}

variable "admin_aws_account_id" { type = string }