variable "rds" {
  type = object({
    role = object({
      name = string
    })
    password = string
    username = string
  })
  sensitive = true
}

variable "s3" {
  type = object({
    buckets = object({
      rds = object({
        arn = string
      })
    })
  })
}