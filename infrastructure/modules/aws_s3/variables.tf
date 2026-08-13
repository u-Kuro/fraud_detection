variable "iam" {
  type = object({
    users = object({
      teams = map(object({
        role = object({
          name = string
        })
      }))
    })
  })
}

variable "mwaa" {
  type = object({
    users = object({
      teams = set(string)
    })
  })
}

variable "s3" {
  type = object({
    users = object({
      teams = set(string)
    })
  })
}