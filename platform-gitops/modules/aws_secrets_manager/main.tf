resource "aws_secretsmanager_secret" "mle_runtime" {
  name                    = "/mle"
  recovery_window_in_days = 0
}

# resource "aws_secretsmanager_secret_version" "mle_runtime" {
#   secret_id     = aws_secretsmanager_secret.mle_runtime.id
#   secret_string = jsonencode(local.mle_runtime_secret)
# }