output "admin" {
  value = {
    account_id  = data.aws_caller_identity.admin.account_id
    arn         = data.aws_caller_identity.admin.arn
  }
}

output "teams" {
  value = {
    for team in var.teams : team => {
      access_keys = {
        aws_access_key = aws_iam_access_key.teams[team].id
        aws_secret_key = aws_iam_access_key.teams[team].secret
      }
      role = {
        arn = aws_iam_role.teams[team].arn
      }
    }
  }
  sensitive = true
}

output "services" {
  value = {
    ec2 = {
      name  = aws_iam_role.ec2.name
      arn   = aws_iam_role.ec2.arn
    }
    eks = {
      name  = aws_iam_role.eks.name
      arn   = aws_iam_role.eks.arn
    }
    mwaa = {
      name  = aws_iam_role.mwaa.name
      arn   = aws_iam_role.mwaa.arn
    }
    rds = {
      name  = aws_iam_role.rds.name
      arn   = aws_iam_role.rds.arn
    }
  }
}