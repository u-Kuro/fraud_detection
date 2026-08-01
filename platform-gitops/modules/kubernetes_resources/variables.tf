variable "teams" {
  description = "Multi-tenant team definitions"
  type = map(object({
    namespace               = string
    shared_configmap_access = optional(bool, false)
    pg_schema               = optional(string)
    pg_username             = optional(string)
    pg_password             = optional(string)
    s3_bucket               = optional(string)
    mlflow_workspace        = optional(string)
    has_mwaa_access         = optional(bool, false)
  }))
}

variable "team_role_arns" {
  description = "Map of team name → IRSA IAM role ARN (output from aws_iam_oidc module)"
  type        = map(string)
}

# ── Shared platform values injected into ConfigMaps ──────────────────────────
variable "rds_host"           { type = string }
variable "rds_port"           { type = number }
variable "rds_db_name"        { type = string }
variable "aws_region"         { type = string }
variable "s3_endpoint_url"    { type = string }
variable "mlflow_tracking_uri" { type = string }
variable "mwaa_webserver_url" { type = string }
