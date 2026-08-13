output "users" {
  value = {
    teams = {
      for k, v in local.ssm_parameter_users.teams : k => {
        path = v.path
      }
    }
  }
}
