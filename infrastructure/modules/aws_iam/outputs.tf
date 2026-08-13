output "users" {
  value = {
    admin = {
      account_id = data.aws_caller_identity.admin.account_id
      arn        = data.aws_caller_identity.admin.arn
      region     = data.aws_region.admin.region
    }
    teams = {
      for k in local.iam.users.teams : k => {
        password = aws_iam_access_key.teams[k].secret
        role = {
          arn  = aws_iam_role.teams[k].arn
          name = aws_iam_role.teams[k].name
        }
        username = aws_iam_access_key.teams[k].id
      }
    }
  }
  sensitive = true
}

output "services" {
  value = {
    ec2 = {
      arn  = aws_iam_role.ec2.arn
      name = aws_iam_role.ec2.name
    }
    eks = {
      arn  = aws_iam_role.eks.arn
      name = aws_iam_role.eks.name
    }
    mwaa = {
      arn  = aws_iam_role.mwaa.arn
      name = aws_iam_role.mwaa.name
    }
    rds = {
      arn  = aws_iam_role.rds.arn
      name = aws_iam_role.rds.name
    }
  }
}