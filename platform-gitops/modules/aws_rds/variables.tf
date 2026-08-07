variable "rds" {
  type = object({
    role = object({
      arn = string
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