variable "aws" {
  type = object({
    users = object({
      admin = object({
        account_id = string
      })
      ecr_teams = map(object({
        role = object({
          arn = string
        })
      }))
    })
  })
}