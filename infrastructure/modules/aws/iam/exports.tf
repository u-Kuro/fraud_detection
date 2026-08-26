# Allow admin to see teams' IAM credentials
resource "aws_secretsmanager_secret" "teams_iam_credentials" {
  for_each                = var.iam_teams
  name                    = "admin/iam/users/${each.key}/credential"
  recovery_window_in_days = 0

  depends_on = [
    aws_iam_access_key.teams
  ]
}
resource "aws_secretsmanager_secret_version" "teams_iam_credentials" {
  for_each  = aws_secretsmanager_secret.teams_iam_credentials
  secret_id = each.value.id

  secret_string_wo = jsonencode({
    access_key_id     = aws_iam_access_key.teams[each.key].id
    secret_access_key = aws_iam_access_key.teams[each.key].secret
  })
  secret_string_wo_version = 1
}