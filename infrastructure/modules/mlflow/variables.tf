variable "iam" {
  type = object({
    users = object({
      admin = object({
        password = string
        region   = string
        username = string
      })
    })
  })
  sensitive = true
}

variable "elb" {
  type = object({
    alb = object({
      dns_name = string
    })
  })
}

variable "mlflow" {
  type = object({
    flask_server_secret_key = string
    host                    = optional(string, "mlflow")
    port = object({
      container = optional(number, 8080)
    })
    users = object({
      admin = object({
        password = string
        username = string
      })
      teams = set(string)
    })
  })
  sensitive = true
}

variable "rds" {
  type = object({
    postgres = object({
      db_name = string
      host    = string
      port    = number
      users = object({
        mlflow = object({
          password = string
          username = string
        })
      })
    })
  })
  sensitive = true
}

variable "s3" {
  type = object({
    buckets = object({
      mlflow = object({
        arn  = string
        name = string
      })
    })
    url = object({
      egress = string
    })
  })
}