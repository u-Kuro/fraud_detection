variable "rds" {
  type = object({
    db_name  = string
    username = string
    users = object({
      mlflow = object({
        password = string
        username = string
      })
    })
  })
  sensitive = true
}

variable "aws" {
  type = object({
    users = object({
      postgresql_teams = set(string)
    })
  })
}