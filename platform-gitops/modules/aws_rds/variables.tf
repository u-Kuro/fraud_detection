variable "db_identifier" {
  type    = string
  default = "rds"
}
variable "db_username" {
  type = string
}
variable "db_password" {
  type      = string
  sensitive = true
}