variable "region" {
  type = string
}

variable "repositories" {
  type = list(string)
  default = [
    "fraud_detection",
    "drift_monitor",
    "training_pipeline",
    "archiving",
  ]
}