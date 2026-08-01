variable "aws_account_id" { type = string }
variable "aws_region"     { type = string }

variable "eks_oidc_issuer_url" {
  description = "OIDC issuer URL from aws_eks_cluster.main.identity[0].oidc[0].issuer"
  type        = string
}

variable "teams" {
  description = "Multi-tenant team definitions (must match the root teams variable)"
  type = map(object({
    namespace        = string
    ecr_repos        = optional(list(string), [])
    has_mwaa_access  = optional(bool, false)
    s3_team_bucket   = optional(string)
    shared_s3_paths  = optional(list(string), [])
  }))
}

variable "shared_s3_bucket" {
  description = "Name of the shared S3 bucket accessed via team-scoped paths"
  type        = string
}

variable "mwaa_environment_name" {
  description = "Name of the MWAA environment"
  type        = string
  default     = "mwaa"
}
