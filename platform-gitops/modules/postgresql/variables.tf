variable "db_owner_username" {
  type      = string
  sensitive = true
}
variable "db_name" {
  type      = string
  sensitive = true
}

variable "mlflow_db_username" {
  type      = string
  sensitive = true
}
variable "mlflow_db_password" {
  type      = string
  sensitive = true
}

variable "mle_db_username" {
  type      = string
  sensitive = true
}
variable "mle_password" {
  type      = string
  sensitive = true
}

variable "mle_migrations_db_username" {
  type      = string
  sensitive = true
}
variable "mle_migrations_db_password" {
  type      = string
  sensitive = true
}