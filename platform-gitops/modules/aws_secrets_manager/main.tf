# ── Per-team secrets access (own secrets path) ────────────────────────────────
resource "aws_iam_policy" "team_secrets_access" {
  for_each    = var.teams
  name        = "${each.key}_secrets_access"
  description = "${each.key} team access to /secrets/${each.key}/*"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "${each.key}SecretsAccess"
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
        Resource = "arn:aws:secretsmanager:*:${var.aws_account_id}:secret:/secrets/${each.key}/*"
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "team_secrets_access" {
  for_each   = aws_iam_policy.team_secrets_access
  name       = "${each.key}_secrets_access"
  policy_arn = each.value.arn
  users      = []
  roles      = []
  groups     = []
  # Attach to the team IAM role in production:
  # roles = [var.team_role_names[each.key]]
  depends_on = [aws_iam_policy.team_secrets_access]
}

# ── MWAA Airflow connections/variables access (per-team scoped paths) ─────────
# The MWAA Secrets Manager backend reads airflow/connections/<team>/<conn_id>
# and airflow/variables/<team>/<var_key>.
resource "aws_iam_policy" "team_airflow_secrets" {
  for_each    = { for k, v in var.teams : k => v if v.has_mwaa_access }
  name        = "${each.key}_airflow_secrets"
  description = "${each.key} team Airflow connections and variables"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "${each.key}AirflowSecrets"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:airflow/connections/${each.key}/*",
          "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:airflow/variables/${each.key}/*",
        ]
      }
    ]
  })
}