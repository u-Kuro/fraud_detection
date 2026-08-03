variable "teams" {
  type = map(object({
    name = string
  }))
}
variable "aws_account_id" { type = string }