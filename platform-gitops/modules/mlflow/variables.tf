variable "aws" {
  type = object({
    users = object({
      admin = object({
        access_key = string
        region     = string
        secret_key = string
      })
      mlflow_teams = set(string)
    })
  })
  sensitive = true
}

variable "lb" {
  type = object({
    dns_name = string
  })
}

variable "mlflow" {
  type = object({
    flask_server_secret_key = string
    host                    = optional(string, "mlflow")
    port                    = optional(number, 8080)
    users = object({
      admin = object({
        password = string
        username = string
      })
    })
  })
  sensitive = true
}

variable "rds" {
  type = object({
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
    network = object({
      endpoint_url = string
    })
  })
}