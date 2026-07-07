# IAM policy — grants the MLE team (only) read/write access to their secrets.
# Platform team cannot read these secrets; they have no need to.
resource "aws_iam_policy" "mle_secrets_access" {
  name        = "mle_secrets_access"
  description = "MLE team full self-service access under /mle/* namespace."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "mle_secret_access"
        Effect = "Allow"
        Action = [
          "secretsmanager:CreateSecret",
          "secretsmanager:DeleteSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecret",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
        ]
        Resource = "arn:aws:secretsmanager:*:${var.aws_account_id}:secret:/mle/*"
      },
      {
        Sid      = "mle_secret_list_access"
        Effect   = "Allow"
        Action   = ["secretsmanager:ListSecrets"]
        Resource = "*"   # ListSecrets can't be scoped to a prefix
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