variable "aws" {
  type = object({
    users = object({
      teams = map(object({
        role = object({
          arn = string
        })
      }))
      mwaa_teams = set(string)
    })
  })
}