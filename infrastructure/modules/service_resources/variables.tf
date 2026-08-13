variable "iam" {
  type = object({
    users = object({
      admin = object({
        region = string
      })
      teams = map(object({
        password = string
        username = string
      }))
    })
  })
  sensitive = true
}

variable "ecr" {
  type = object({
    aws = object({
      endpoint = string
      token = object({
        authorization_token = string
        password            = string
        username            = string
      })
    })
  })
  sensitive = true
}

variable "eks" {
  type = object({
    users = object({
      teams = map(object({
        kubernetes = object({
          namespace = string
        })
      }))
    })
  })
}

variable "mlflow" {
  type = object({
    url = object({
      ingress  = string
      internal = string
    })
    users = object({
      teams = map(object({
        password = string
        username = string
      }))
    })
  })
}

variable "mwaa" {
  type = object({
    url = object({
      egress = string
    })
    users = object({
      teams = map(object({
        environment = object({
          name = string
        })
        connections = object({
          prefix = string
        })
        variables = object({
          prefix = string
        })
      }))
    })
  })
}

variable "rds" {
  type = object({
    postgres = object({
      host    = string
      port    = number
      db_name = string
      users = object({
        teams = map(object({
          username = string
          password = string
        }))
      })
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