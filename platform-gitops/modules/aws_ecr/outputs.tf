output "team_repository_urls" {
  value = { for v in values(aws_ecr_repository.team_repositories) : v.name => v.repository_url }
}