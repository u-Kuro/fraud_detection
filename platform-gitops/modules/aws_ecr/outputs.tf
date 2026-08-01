output "repository_urls" {
  description = "Map of '<team>/<repo>' → ECR repository URL"
  value       = { for k, v in aws_ecr_repository.team_repos : k => v.repository_url }
}