# INPUTS
locals {
  aws = var.aws
}
# COMPUTED
locals {
  # ECR TEAMS' REPOSITORIES
  ecr_teams_repositories = toset(flatten([
    for team, values in local.aws.users.teams : [
      for repository in values.ecr.repositories :
      "${team}/${repository}"
    ]
  ]))
}