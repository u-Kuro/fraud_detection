variable "iam" {
  type = object({
    users = object({
      admin = object({
        account_id = string
      })
      teams = map(object({
        role = object({
          arn  = string
          name = string
        })
      }))
    })
  })
}

variable "local_files" {
  type = object({
    directory = object({
      path = string
    })
    mwaa_requirements = object({
      file = object({
        path = string
      })
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
    users = object({
      teams = set(string)
    })
  })
}

variable "s3" {
  type = object({
    buckets = object({
      teams_mwaa = map(object({
        arn  = string
        name = string
      }))
    })
  })
}

variable "secrets_manager" {
  type = object({
    container = object({
      endpoint_url = string
    })
  })
}

variable "ssm_parameter" {
  type = object({
    users = object({
      teams = map(object({
        path = string
      }))
    })
  })
}