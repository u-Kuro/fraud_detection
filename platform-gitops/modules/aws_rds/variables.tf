variable "db_identifier" {
  type    = string
  default = "fraud-detection-rds"
}
variable "db_username" {
  type = string
}
variable "db_password" {
  type      = string
  sensitive = true
}