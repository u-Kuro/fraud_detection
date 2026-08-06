variable "teams" {
  type = map(object({
    role = object({
      arn = string
    })
    ecr = object({
      repositories = set(string)
    })
  }))
}

variable "aws_admin" {
  type = object({
    account_id = string
  })
}