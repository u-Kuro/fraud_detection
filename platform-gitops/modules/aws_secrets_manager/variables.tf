variable "aws_account_id" { type = string }
variable "aws_region"     { type = string }

variable "teams" {
  description = "Team definitions"
  type = map(object({
    has_mwaa_access = optional(bool, false)
  }))
  default = {}
}