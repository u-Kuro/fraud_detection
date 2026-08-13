variable "rds" {
  type = object({
    postgres = object({
      password = string
      username = string
    })
    role = object({
      name = string
    })
  })
  sensitive = true
}

variable "s3" {
  type = object({
    buckets = object({
      postgres = object({
        arn = string
      })
    })
  })
}