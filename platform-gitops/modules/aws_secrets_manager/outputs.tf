output "mle_runtime_secret_arn" {
  value = aws_secretsmanager_secret.mle_runtime.arn
}
output "fraud_api_secret_arn" {
  value = aws_secretsmanager_secret.fraud_api.arn
}
output "mle_secrets_policy_arn" {
  value = aws_iam_policy.mle_secrets_access.arn
}