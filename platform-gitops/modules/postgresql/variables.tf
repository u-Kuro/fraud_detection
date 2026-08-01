variable "db_owner_username" { type = string  sensitive = true }
variable "db_name"           { type = string  sensitive = true }

variable "mlflow_postgresql_username" {
  type      = string
  sensitive = true
}
variable "mlflow_postgresql_password" {
  type      = string
  sensitive = true
}

variable "teams" {
  description = "Team definitions — only pg_* fields are used here"
  type = map(object({
    pg_schema              = optional(string)
    pg_username            = optional(string)
    pg_password            = optional(string)
    pg_migrations_username = optional(string)
    pg_migrations_password = optional(string)
  }))
  default = {}
}