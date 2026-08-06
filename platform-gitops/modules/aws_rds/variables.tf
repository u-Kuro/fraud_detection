variable "db" {
  type = object({
    username = string
    password = string
  })
  sensitive = true
}

variable "rds" {
  type = object({
    role = object({
      arn = string
    })
  })
}

variable "s3" {
  type = object({
    rds_bucket = object({
      arn = string
    })
  })
}