variable "aws" {
  type = object({
    users = object({
      admin = object({
        arn        = string
        access_key = string
        region     = string
        secret_key = string
      })
      teams = map(object({
        kubernetes = object({
          namespace = string
        })
        role = object({
          arn = string
        })
      }))
    })
  })
  sensitive = true
}

variable "ec2" {
  type = object({
    role = object({
      arn  = string
      name = string
    })
  })
}

variable "ecr" {
  type = object({
    container = object({
      endpoint     = string
      endpoint_url = string
    })
    aws = object({
      endpoint = string
    })
    password = string
    username = string
  })
  sensitive = true
}

variable "eks" {
  type = object({
    host = object({
      endpoint_url = string
    })
    role = object({
      arn  = string
      name = string
    })
  })
}

variable "local_files" {
  type = object({
    kubeconfig = object({
      host = object({
        file = object({
          path = string
        })
      })
    })
    directory = object({
      path = string
    })
  })
}

