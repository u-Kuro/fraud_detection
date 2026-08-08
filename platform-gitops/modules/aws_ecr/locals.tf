# INPUTS
locals {
  aws = var.aws
}
# COMPUTED
locals {
  # TEAM REPOSITORIES
  team_repositories = toset(flatten([
    for team, values in local.aws.users.teams : [
      for repository in values.ecr.repositories :
      "${team}/${repository}"
    ]
  ]))
}