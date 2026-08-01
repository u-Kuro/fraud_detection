variable "teams" {
  description = "Team definitions — only s3_team_bucket is used here"
  type = map(object({
    s3_team_bucket = optional(string)
  }))
  default = {}
}
