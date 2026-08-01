# ─────────────────────────────────────────────────────────────────────────────
# TEAM REGISTRY — add a new team here; everything else is driven by for_each.
# ─────────────────────────────────────────────────────────────────────────────
locals {
  teams = set(
    "mle",
    # "example_future_team"
  )
}

# ── IAM User per team ────────────────────────────────────────────────────────
resource "aws_iam_user" "team" {
  for_each = local.teams
  name     = each.key
}

# ── IAM Access Key per team (static credentials for CI/CD) ───────────────────
resource "aws_iam_access_key" "team" {
  for_each = local.teams
  user     = aws_iam_user.team[each.key].name
}

# ── IAM Role per team — other modules attach service policies to this role ───
# The team's IAM user is trusted to assume this role via STS.
# MiniStack: simulated — role and trust policy are stored but STS is not enforced.
resource "aws_iam_role" "team" {
  for_each = local.teams
  name     = "${each.key}_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowTeamUserToAssume"
        Effect = "Allow"
        Principal = {
          AWS = aws_iam_user.team[each.key].arn
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# ── ECR GetAuthorizationToken (global, not repo-scoped) ──────────────────────
# Must be attached here because it cannot be scoped to a specific repository ARN.
resource "aws_iam_role_policy" "team_ecr_auth" {
  for_each = local.teams
  name     = "${each.key}_ecr_auth"
  role     = aws_iam_role.team[each.key].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "AllowECRLogin"
        Effect   = "Allow"
        Action   = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      }
    ]
  })
}

# ── Store access key + secret in Secrets Manager for CI/CD retrieval ─────────
resource "aws_secretsmanager_secret" "team_credentials" {
  for_each = local.teams
  name     = "/teams/${each.key}/credentials"
}

resource "aws_secretsmanager_secret_version" "team_credentials" {
  for_each  = local.teams
  secret_id = aws_secretsmanager_secret.team_credentials[each.key].id

  secret_string = jsonencode({
    access_key_id     = aws_iam_access_key.team[each.key].id
    secret_access_key = aws_iam_access_key.team[each.key].secret
    role_arn          = aws_iam_role.team[each.key].arn
  })
}