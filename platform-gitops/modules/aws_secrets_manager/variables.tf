variable "rds_db_address" { type = string }
variable "rds_db_port" { type = string }
variable "rds_db_name" { type = string }

variable "mle_db_username" { 
  type = string
  sensitive = true
}
variable "mle_db_password" { 
  type = string
  sensitive = true
}

variable "s3_endpoint_url" { type = string }
variable "s3_access_key" { 
  type = string
  sensitive = true
}
variable "s3_secret_key" { 
  type = string
  sensitive = true
}
variable "s3_aws_region"    { type = string }
variable "s3_mlflow_bucket" { type = string }
variable "s3_mle_bucket"    { type = string }

variable "mlflow_tracking_uri" { type = string }
variable "fraud_api_url" { type = string }

variable "slack_bot_token" { 
  type = string
  sensitive = true
}
variable "slack_app_token" { 
  type = string
  sensitive = true
}
variable "slack_channel_id" { type = string }
variable "slack_signing_secret" { 
  type = string
  sensitive = true
}

variable "mlflow_model_uri" {
  type = string
  default = "models:/XGBoost@production"
}