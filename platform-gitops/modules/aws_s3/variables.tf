variable "teams" {
  type = map(object({
    role = object({
      arn = string
    })
  }))
}