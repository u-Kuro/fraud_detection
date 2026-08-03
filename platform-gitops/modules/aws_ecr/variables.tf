variable "aws_account_id" { type = string }

variable "teams" {
  type = map(object({
    ecr_repositories = set(string)
    name             = string
    arn              = string
  }))
}