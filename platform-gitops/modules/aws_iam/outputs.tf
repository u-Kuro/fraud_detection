output "admin_identity" {
  value = {
    id = data.aws_caller_identity.admin.id
    account_id = data.aws_caller_identity.admin.account_id
    arn = data.aws_caller_identity.admin.arn
  }
}

output "team_access_keys" {
  value = {
    for k, v in aws_iam_access_key.teams : k => {
      aws_access_key = v.id
      aws_secret_key = v.secret
    }
  }
  sensitive = true
}

output "team_users" {
  value = {
    for k, v in aws_iam_user.teams : k => {
      name = v.name
      arn = v.arn
    }
  }
}