variable "aws" {
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
        username            = string
        password            = string
        authorization_token = string
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
      egress  = string
      ingress = string
    })
    users = object({
      teams = map(object({
        username = string
        password = string
      }))
    })
  })
}

variable "mwaa" {
  type = object({
    url = object({
      egress = string
    })
    dag_s3_uri = string
    users = object({
      teams = map(object({
        environment = object({
          name = string
        })
        connections = object({
          prefix = string
        })
      }))
    })
  })
}

variable "rds" {
  type = object({
    postgresql = object({
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