# IAM
# /admin
output "admin_arn" { value = data.aws_caller_identity.admin.arn }
output "admin_account_id" { value = data.aws_caller_identity.admin.account_id }
output "admin_region" { value = data.aws_region.admin.region }
# /teams
output "teams" { value = var.iam_teams }
output "teams_names" { value = { for k, v in aws_iam_user.teams : k => v.name } }
output "teams_role_arns" { value = { for k, v in aws_iam_user.teams : k => v.arn } }
# /ec2
output "ec2_role_name" { value = aws_iam_role.ec2.name }
output "ec2_role_arn" { value = aws_iam_role.ec2.arn }
# /eks
output "eks_role_name" { value = aws_iam_role.eks.name }
output "eks_role_arn" { value = aws_iam_role.eks.arn }
# /mwaa
output "mwaa_role_name" { value = aws_iam_role.mwaa.name }
output "mwaa_role_arn" { value = aws_iam_role.mwaa.arn }
# /rds
output "rds_role_name" { value = aws_iam_role.rds.name }
output "rds_role_arn" { value = aws_iam_role.rds.arn }