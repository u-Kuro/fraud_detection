output "users" {
  value = {
    teams = toset(keys(aws_iam_role_policy.teams_ecr))
  }
}
