output "mle_pipeline_secret_arn" {
  value = aws_secretsmanager_secret.mle_pipeline.arn
}
output "mle_fraud_detection_secret_arn" {
  value = aws_secretsmanager_secret.mle_fraud_detection.arn
}
output "mle_secrets_policy_arn" {
  value = aws_iam_policy.mle_secrets_access.arn
}