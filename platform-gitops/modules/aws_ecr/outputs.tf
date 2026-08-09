output "team_repository_urls" {
  value = {
    for v in values(aws_ecr_repository.ecr_teams) :
    v.name => v.repository_url
  }
}