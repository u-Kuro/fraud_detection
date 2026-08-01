# Keyed by "<team>/<repo>", e.g. { "mle/fraud_detection" = "000000000000.dkr.ecr.us-east-1.amazonaws.com/mle/fraud_detection" }
output "repository_urls" {
  value = { for k, v in aws_ecr_repository.repos : k => v.repository_url }
}

# Per-team map for downstream consumers: { mle = { fraud_detection = "...", archive = "..." } }
output "team_repository_urls" {
  value = {
    for team in keys(local.team_repositories) : team => {
      for k, v in aws_ecr_repository.repos : split("/", k)[1] => v.repository_url
      if split("/", k)[0] == team
    }
  }
}