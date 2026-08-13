variable "rds" {
  type = object({
    db_name  = string
    username = string
    users = object({
      mlflow = object({
        password = string
        username = string
      })
      teams = set(string)
    })
  })
  sensitive = true
}