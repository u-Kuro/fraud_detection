variable "aws" {
  type = object({
    users = object({
      teams = set(string)
    })
  })
}