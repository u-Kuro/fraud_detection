resource "aws_secretsmanager_secret" "mle_pipeline" {
  name                    = "/mle/pipeline"
  description             = "Runtime credentials for MLE DAG containers (drift_monitor, training_pipeline, archiving)."
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret" "mle_fraud_detection" {
  name                    = "/mle/fraud_detection"
  description             = "Runtime credentials for the fraud_detection service."
  recovery_window_in_days = 0
}

# IAM policy — grants the MLE team (only) read/write access to their secrets.
# Platform team cannot read these secrets; they have no need to.
resource "aws_iam_policy" "mle_secrets_access" {
  name        = "mle_secrets_access"
  description = "Grants MLE team read/write access to their own Secrets Manager entries."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "mle_secret_access"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecret",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
        ]
        Resource = [
          aws_secretsmanager_secret.mle_pipeline.arn,
          aws_secretsmanager_secret.mle_fraud_detection.arn,
        ]
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "mle_secrets_access" {
  name       = "mle_secrets_access"
  policy_arn = aws_iam_policy.mle_secrets_access.arn
  users      = []
  roles      = []
  groups     = []
  # In a real deployment, specify the MLE IAM group/role here.
  # Ministack: the policy attachment exists but enforcement is simulated.
}