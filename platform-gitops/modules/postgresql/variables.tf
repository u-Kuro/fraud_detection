variable "db_owner_username" {
  type      = string
  sensitive = true
}
variable "db_name" {
  type      = string
  sensitive = true
}

variable "mlflow_postgresql_username" {
  type      = string
  sensitive = true
}
variable "mlflow_postgresql_password" {
  type      = string
  sensitive = true
}

variable "postgresql_teams" {
  type = set(string)
}