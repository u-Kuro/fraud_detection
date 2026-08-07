variable "aws" {
  type = object({
    users = object({
      admin = object({
        account_id = string
      })
      teams = map(object({
        role = object({
          arn = string
        })
      }))
    })
  })
}