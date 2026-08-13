# TEAMS CREDENTIAL
resource "aws_secretsmanager_secret" "teams_iam_credential" {
  for_each                = local.iam.users.teams
  name                    = "IAM/teams/${each.key}/credential"
  recovery_window_in_days = 0
}
resource "aws_secretsmanager_secret_version" "teams_iam_credential" {
  for_each  = aws_secretsmanager_secret.teams_iam_credential
  secret_id = each.value.id

  secret_string_wo = jsonencode({
    access_key_id     = aws_iam_access_key.teams[each.key].id
    secret_access_key = aws_iam_access_key.teams[each.key].secret
  })
  secret_string_wo_version = 1

  depends_on = [
    aws_iam_access_key.teams,
    aws_secretsmanager_secret.teams_iam_credential
  ]
}