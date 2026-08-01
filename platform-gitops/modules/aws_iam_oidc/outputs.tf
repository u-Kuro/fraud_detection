output "oidc_provider_arn" {
  description = "ARN of the IAM OIDC provider"
  value       = aws_iam_openid_connect_provider.eks.arn
}

output "team_role_arns" {
  description = "Map of team name → IRSA role ARN"
  value       = { for k, v in aws_iam_role.team : k => v.arn }
}
