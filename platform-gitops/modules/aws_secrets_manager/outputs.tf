output "team_secrets_policy_arns" {
  description = "Map of team name → secrets IAM policy ARN"
  value       = { for k, v in aws_iam_policy.team_secrets_access : k => v.arn }
}

output "team_airflow_secrets_policy_arns" {
  description = "Map of team name → Airflow secrets IAM policy ARN"
  value       = { for k, v in aws_iam_policy.team_airflow_secrets : k => v.arn }
}