variable "iam" {
  type = object({
    users = object({
      admin = object({
        account_id = string
      })
      teams = map(object({
        role = object({
          name = string
        })
      }))
    })
  })
}

variable "ssm_parameter" {
  type = object({
    users = object({
      teams = set(string)
    })
  })
}