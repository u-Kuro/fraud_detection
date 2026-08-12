variable "iam" {
  type = object({
    users = object({
      admin = object({
        arn      = string
        username = string
        region   = string
        password = string
      })
      teams = map(object({
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
    users = object({
      teams = map(object({
        kubernetes = object({
          namespace = string
        })
      }))
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

