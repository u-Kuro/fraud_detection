variable "teams" {
  type = map(object({
    role = object({
      arn = string
    })
  }))
}

variable "aws_admin" {
  type = object({
    account_id = string
  })
}