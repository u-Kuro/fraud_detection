# map of team_key => IAM Role ARN — consumed by every other service module
output "team_role_arns" {
  value = { for k, v in aws_iam_role.team : k => v.arn }
}

output "team_user_arns" {
  value = { for k, v in aws_iam_user.team : k => v.arn }
}

# sensitive — not printed in plan output
output "team_access_key_ids" {
  value     = { for k, v in aws_iam_access_key.team : k => v.id }
  sensitive = true
}
output "team_secret_access_keys" {
  value     = { for k, v in aws_iam_access_key.team : k => v.secret }
  sensitive = true
}