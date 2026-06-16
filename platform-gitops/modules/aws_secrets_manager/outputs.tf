output "mle_runtime_secret_arn" {
  value = aws_secretsmanager_secret.mle_runtime.arn
}

output "fraud_api_secret_arn" {
  value = aws_secretsmanager_secret.fraud_api.arn
}