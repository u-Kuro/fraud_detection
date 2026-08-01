variable "teams" {
  description = "Team definitions — only ecr_repos and the matching role ARN are used here"
  type = map(object({
    ecr_repos = optional(list(string), [])
  }))
}

variable "team_role_arns" {
  description = "Map of team name → IRSA role ARN (from aws_iam_oidc module)"
  type        = map(string)
}
