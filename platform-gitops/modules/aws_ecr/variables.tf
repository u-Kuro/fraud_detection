variable "region" {
  type = string
}

variable "repositories" {
  type = list(string)
  default = [
    "fraud-detection-api",
    "fraud-detection-drift-monitor",
    "fraud-detection-training-pipeline",
    "fraud-detection-archiving",
  ]
}