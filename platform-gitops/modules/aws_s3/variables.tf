variable "teams" {
  type = map(object({
    role_arn = string
  }))
}