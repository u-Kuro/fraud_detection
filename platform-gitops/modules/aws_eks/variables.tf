variable "eks" {
  type = object({
    role = object({
      arn  = string
      name = string
    })
    host = object({
      endpoint_url = string
    })
  })
}

variable "ec2" {
  type = object({
    role = object({
      arn  = string
      name = string
    })
  })
}

variable "aws_admin" {
  type = object({
    arn        = string
    region     = string
    access_key = string
    secret_key = string
  })
  sensitive = true
}

variable "teams" {
  type = map(object({
    role = object({
      arn = string
    })
    kubernetes = object({
      namespace = string
    })
  }))
}

variable "local_files" {
  type = object({
    directory = object({
      path = string
    })
  })
}

variable "ecr" {
  type = object({
    username = string
    password = string
    host = object({
      endpoint = string
    })
    container = object({
      endpoint     = string
      endpoint_url = string
    })
  })
  sensitive = true
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