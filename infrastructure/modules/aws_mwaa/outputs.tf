output "url" {
  value = {
    egress = "http://${local.ministack.ip}:4566"
  }
}

output "users" {
  value = {
    teams = {
      for k, v in aws_mwaa_environment.teams : k => {
        environment = {
          name = v.name
        }
        connections = {
          prefix = v.airflow_configuration_options["secrets.backend_kwargs"].connections_prefix
        }
        variables = {
          prefix = v.airflow_configuration_options["secrets.backend_kwargs"].variables_prefix
        }
      }
    }
  }
}