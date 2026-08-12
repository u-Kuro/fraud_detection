output "admin" {
  value = {
    account_id = data.aws_caller_identity.admin.account_id
    arn        = data.aws_caller_identity.admin.arn
    region     = data.aws_region.admin.region
  }
}

output "teams" {
  value = {
    for k in local.aws.users.teams : k => {
      access_keys = {
        aws_access_key = aws_iam_access_key.teams[k].id
        aws_secret_key = aws_iam_access_key.teams[k].secret
      }
      role = {
        arn  = aws_iam_role.teams[k].arn
        name = aws_iam_role.teams[k].name
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