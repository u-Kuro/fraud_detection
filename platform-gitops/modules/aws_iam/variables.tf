variable "iam" {
  type = object({
    users = object({
      teams = set(string)
    })
  })
}