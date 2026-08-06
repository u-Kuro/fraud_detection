variable "s3" {
  type = object({
    mwaa_bucket = object({
      arn  = string
      name = string
    })
  })
}

variable "kubeconfig" {
  type = object({
    host = object({
      file = object({
        path = string
      })
    })
  })
}

variable "mwaa" {
  type = object({
    role = object({
      arn = string
    })
  })
}

variable "aws_admin" {
  type = object({
    accout_id = string
  })
  sensitive = true
}

variable "secretsmanager" {
  type = object({
    container = object({
      endpoint_url = string
    })
  })
}

variable "teams" {
  type = map(object({
    role = object({
      arn = string
    })
  }))
}