variable "aws" {
  type = object({
    users = object({
      mwaa_teams = set(string)
      teams = map(object({
        role = object({
          arn = string
        })
      }))
    })
  })
}