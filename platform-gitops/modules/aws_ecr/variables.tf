variable "aws" {
  type = object({
    users = object({
      admin = object({
        account_id = string
      })
      teams = map(object({
        ecr = object({
          repositories = set(string)
        })
        role = object({
          arn = string
        })
      }))
    })
  })
}