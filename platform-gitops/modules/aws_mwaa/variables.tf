variable "aws" {
  type = object({
    users = object({
      admin = object({
        account_id = string
      })
      mwaa_teams = map(object({
        role = object({
          arn = string
        })
      }))
    })
  })
  sensitive = true
}

variable "local_files" {
  type = object({
    directory = object({
      path = string
    })
    kubeconfig = object({
      container = object({
        file = object({
          path = string
        })
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

variable "s3" {
  type = object({
    buckets = object({
      mwaa_teams = map(object({
        arn = string
      }))
    })
  })
}

variable "secretsmanager" {
  type = object({
    container = object({
      endpoint_url = string
    })
  })
}