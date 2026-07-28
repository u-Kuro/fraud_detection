variable "region" {
  type = string
}

variable "repositories" {
  type = list(string)
  default = [
    "fraud_detection",
    "drift_check",
    "train_model",
    "archive",
  ]
}