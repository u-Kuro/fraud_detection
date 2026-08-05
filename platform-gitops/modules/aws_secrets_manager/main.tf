data "aws_iam_policy" "secretsmanager_read_write" {
  name = "SecretsManagerReadWrite"
}
resource "aws_iam_user_policy" "teams" {
  for_each = var.teams
  name     = "${each.key}_secretsmanager_policy"
  user     = each.value.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid     = "SMOwnConnections"
        Effect  = "Allow"
        Action  = [
          "secretsmanager:CreateSecret",
          "secretsmanager:DeleteSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecret",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
        ]
        Resource = ["arn:aws:secretsmanager:*:${var.aws_account_id}:secret:${each.key}/*"]
      }
    ]
  })
}