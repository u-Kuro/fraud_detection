variable "teams" {
  type = map(object({
    role_arn = string
  }))
}
variable "aws_account_id" { type = string }