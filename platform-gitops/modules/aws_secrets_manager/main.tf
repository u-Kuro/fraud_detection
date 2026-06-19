# IAM role for MLE team CI/CD — the only principal allowed to access MLE secrets.
resource "aws_iam_role" "mle_team" {
  name = "mle-team-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "mle_secret_access" {
  name        = "mle-secret-access-policy"
  description = "Allows MLE team to read and write their own Secrets Manager entries."
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "secretsmanager:GetSecretValue",
        "secretsmanager:PutSecretValue",
        "secretsmanager:UpdateSecret",
        "secretsmanager:DescribeSecret",
      ]
      Resource = [
        aws_secretsmanager_secret.mle_runtime.arn,
        aws_secretsmanager_secret.fraud_api.arn,
      ]
    }]
  })
}

resource "aws_iam_role_policy_attachment" "mle_team" {
  role       = aws_iam_role.mle_team.name
  policy_arn = aws_iam_policy.mle_secret_access.arn
}

# Empty shell — MLE team populates values.
resource "aws_secretsmanager_secret" "mle_runtime" {
  name                    = var.mle_runtime_secret_name
  description             = "Runtime credentials for MLE DAG containers. MLE team manages values."
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret" "fraud_api" {
  name                    = var.fraud_api_secret_name
  description             = "Credentials for fraud_api. MLE team manages values."
  recovery_window_in_days = 0
}

# Resource-based policies: deny GetSecretValue to everyone except the MLE role.
# DevOps can create/delete the secret (admin), but cannot read its values.
resource "aws_secretsmanager_secret_policy" "mle_runtime" {
  secret_arn = aws_secretsmanager_secret.mle_runtime.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowMleTeam"
        Effect    = "Allow"
        Principal = { AWS = aws_iam_role.mle_team.arn }
        Action    = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecret",
          "secretsmanager:DescribeSecret",
        ]
        Resource = "*"
      },
      {
        Sid       = "DenyEveryoneElse"
        Effect    = "Deny"
        Principal = "*"
        Action    = "secretsmanager:GetSecretValue"
        Resource  = "*"
        Condition = {
          StringNotEquals = {
            "aws:PrincipalArn" = aws_iam_role.mle_team.arn
          }
        }
      },
    ]
  })
}

resource "aws_secretsmanager_secret_policy" "fraud_api" {
  secret_arn = aws_secretsmanager_secret.fraud_api.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowMleTeam"
        Effect    = "Allow"
        Principal = { AWS = aws_iam_role.mle_team.arn }
        Action    = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecret",
          "secretsmanager:DescribeSecret",
        ]
        Resource = "*"
      },
      {
        Sid       = "DenyEveryoneElse"
        Effect    = "Deny"
        Principal = "*"
        Action    = "secretsmanager:GetSecretValue"
        Resource  = "*"
        Condition = {
          StringNotEquals = {
            "aws:PrincipalArn" = aws_iam_role.mle_team.arn
          }
        }
      },
    ]
  })
}