output "users" {
  value = {
    teams = {
      for k, v in local.secrets_manager_users.teams : k => {
        path = v.path
      }
    }
  }
}

