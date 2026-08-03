output "admin_identity" {
  value = {
    id = data.aws_caller_identity.admin.id
    account_id = data.aws_caller_identity.admin.account_id
    arn = data.aws_caller_identity.admin.arn
  }
  sensitive = true
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

output "mlflow_access_key" {
  value = {
    aws_access_key = aws_iam_access_key.mlflow.id
    aws_secret_key = aws_iam_access_key.mlflow.secret
  }
  sensitive = true
}

output "mlflow_user" {
  value = {
    name = aws_iam_user.mlflow.name
  }
}