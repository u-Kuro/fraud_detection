variable "aws" {
  type = object({
    users = object({
      admin = object({
        account_id = string
      })
      ecr_teams = map(object({
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