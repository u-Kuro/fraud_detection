variable "aws_region" {
  type = string
}

variable "mlflow_bucket_name" {
  type    = string
  default = "mlflow"
}
variable "mle_bucket_name" {
  type    = string
  default = "mle"
}