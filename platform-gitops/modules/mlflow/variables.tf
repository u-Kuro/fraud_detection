variable "mlflow" {
  type = object({
    host = optional(string, "mlflow")
    port = optional(number, 5000)
    admin = object({
      username = string
      password = string
    })
    flask_server_secret_key = string
  })
  sensitive = true
}

variable "db" {
  type = object({
    host    = string
    port    = number
    db_name = string
    mlflow = object({
      username = string
      password = string
    })
  })
  sensitive = true
}

variable "s3" {
  type = object({
    mlflow_bucket = object({
      arn  = string
      name = string
    })
    network = object({
      endpoint_url = string
    })
  })
}

variable "aws_admin" {
  type = object({
    access_key = string
    secret_key = string
    region     = string
  })
  sensitive = true
}

variable "mlflow_teams" {
  type = set(string)
}