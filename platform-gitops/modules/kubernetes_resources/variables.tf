variable "aws" {
  type = object({
    users = object({
      teams = map(object({
        kubernetes = object({
          namespace = string
        })
      }))
    })
  })
}

variable "ecr" {
  type = object({
    aws = object({
      endpoint = string
      token = object({
        username = string
        password = string
        authorization_token = string
      })
    })
  })
}