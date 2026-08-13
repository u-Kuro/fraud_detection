locals {
  teams = {
    MLE = {
      includes = {
        ECR             = true
        EKS             = true
        MWAA            = true
        S3              = true
        SECRETS_MANAGER = true
        SSM_PARAMETER = true
        MLFLOW          = true
        POSTGRESQL      = true
      }
    }
  }
}

module "iam" {
  source = "./modules/aws_iam"

  iam = {
    users = {
      teams = keys(local.teams)
    }
  }
}

module "ssm_parameter" {
  source = "./modules/aws_ssm_parameter"

  iam = {
    users = {
      admin = {
        account_id = module.iam.users.admin.account_id
      }
      teams = {
        for k, v in local.teams : k => {
          role = {
            name = module.iam.users.teams[k].role.name
          }
        }
      }
    }
  }

  ssm_parameter = {
    users = {
      teams = [
        for k, v in local.teams : k
        if v.includes.SSM_PARAMETER
      ]
    }
  }

  depends_on = [module.iam]
}

module "s3" {
  source = "./modules/aws_s3"

  iam = {
    users = {
      teams = {
        for k, v in local.teams : k => {
          role = {
            name = module.iam.users.teams[k].role.name
          }
        }
      }
    }
  }

  mwaa = {
    users = {
      teams = [
        for k, v in local.teams : k
        if v.includes.MWAA
      ]
    }
  }

  s3 = {
    users = {
      teams = [
        for k, v in local.teams : k
        if v.includes.S3
      ]
    }
  }

  depends_on = [module.iam]
}

module "rds" {
  source = "./modules/aws_rds"

  rds = {
    role = {
      name = module.iam.services.rds.name
    }
    password = var.rds_admin_password
    username = var.rds_admin_username
  }

  s3 = {
    buckets = {
      postgres = {
        arn = module.s3.buckets.postgres.arn
      }
    }
  }

  depends_on = [
    module.iam,
    module.s3
  ]
}

module "postgresql" {
  source = "./modules/postgresql"

  rds = {
    db_name  = module.rds.postgres.db_name
    username = module.rds.postgres.username
    users = {
      mlflow = {
        password = var.mlflow_postgresql_password
        username = var.mlflow_postgresql_username
      }
      teams = [
        for k, v in local.teams : k
        if v.includes.POSTGRESQL
      ]
    }
  }

  depends_on = [
    module.rds
  ]
}

module "secrets_manager" {
  source = "./modules/aws_secrets_manager"

  iam = {
    users = {
      admin = {
        account_id = module.iam.users.admin.account_id
      }
      teams = {
        for k, v in local.teams : k => {
          role = {
            name = module.iam.users.teams[k].role.name
          }
        }
      }
    }
  }

  secrets_manager = {
    users = {
      teams = [
        for k, v in local.teams : k
        if v.includes.SECRETS_MANAGER
      ]
    }
  }

  depends_on = [module.iam]
}

module "ecr" {
  source = "./modules/aws_ecr"

  iam = {
    users = {
      admin = {
        account_id = module.iam.users.admin.account_id
      }
      teams = {
        for k, v in local.teams : k => {
          role = {
            name = module.iam.users.teams[k].role.name
          }
        }
      }
    }
  }

  ecr = {
    users = {
      teams = [
        for k, v in local.teams : k
        if v.includes.ECR
      ]
    }
  }

  depends_on = [module.iam]
}

# Creates local EKS container from local AWS emulator (MiniStack)
# then Copies its k3s.yaml (kubeconfig)
# into Other local emulated services (e.g. MWAA)
# to Allow access to manage cluster resources
module "eks" {
  source = "./modules/aws_eks"

  iam = {
    users = {
      admin = {
        arn      = module.iam.users.admin.arn
        password = var.aws_secret_key
        region   = module.iam.users.admin.region
        username = var.aws_access_key
      }
      teams = {
        for k, team in local.teams : k => {
          role = {
            arn = module.iam.users.teams[k].role.arn
          }
        }
      }
    }
  }

  ec2 = {
    role = {
      arn  = module.iam.services.ec2.arn
      name = module.iam.services.ec2.name
    }
  }

  ecr = {
    container = {
      endpoint     = var.ecr_container_endpoint
      endpoint_url = var.ecr_container_endpoint_url
    }
    aws = {
      endpoint = local.ecr_aws_endpoint
    }
    password = local.ecr_password
    username = local.ecr_username
  }

  eks = {
    host = {
      endpoint_url = var.eks_host_endpoint_url
    }
    role = {
      arn  = module.iam.services.eks.arn
      name = module.iam.services.eks.name
    }
    users = {
      teams = {
        for k, team in local.teams : k => {
          kubernetes = {
            namespace = k
          }
        }
        if team.includes.EKS
      }
    }
  }

  local_files = {
    kubeconfig = {
      host = {
        file = {
          path = local_sensitive_file.kubeconfig_host.filename
        }
      }
    }
    directory = {
      path = local.local_files_directory_path
    }
  }

  depends_on = [
    module.iam,
    local_sensitive_file.kubeconfig_host
  ]
}

module "elb" {
  source = "modules/aws_elb"

  eks = {
    ip = module.eks.cluster.ip
  }

  depends_on = [module.eks]
}

# Creates local MWAA container from local AWS emulator (MiniStack)
# then Copies kubeconfig (k3s.yaml from local EKS container)
# into its local container
# to Allow access to manage cluster resources
module "mwaa" {
  source = "./modules/aws_mwaa"

  iam = {
    users = {
      admin = {
        account_id = module.iam.users.admin.account_id
      }
      teams = {
        for k, v in local.teams : k => {
          role = {
            arn  = module.iam.users.teams[k].role.arn
            name = module.iam.users.teams[k].role.name
          }
        }
      }
    }
  }

  local_files = {
    directory = {
      path = local.local_files_directory_path
    }
    mwaa_requirements = {
      file = {
        path = local_sensitive_file.mwaa_requirements.filename
      }
    }
    kubeconfig = {
      container = {
        file = {
          path = module.eks.local_files.kubeconfig_container.path
        }
      }
    }
  }

  mwaa = {
    users = {
      teams = [
        for k, v in local.teams : k
        if v.includes.MWAA
      ]
    }
  }

  s3 = {
    buckets = {
      teams_mwaa = {
        for k, bucket in module.s3.buckets.teams_mwaa : k => {
          arn  = bucket.arn
          name = bucket.name
        }
      }
    }
  }

  secrets_manager = {
    container = {
      endpoint_url = local.secrets_manager_container_endpoint_url
    }
  }

  depends_on = [
    module.iam,
    local_sensitive_file.mwaa_requirements,
    module.eks,
    module.s3
  ]
}

module "mlflow" {
  source = "modules/mlflow"

  iam = {
    users = {
      admin = {
        password = var.aws_secret_key
        region   = module.iam.users.admin.region
        username = var.aws_access_key
      }
    }
  }

  elb = {
    alb = {
      dns_name = module.elb.alb.dns_name
    }
  }

  mlflow = {
    flask_server_secret_key = var.mlflow_flask_server_secret_key
    users = {
      admin = {
        password = var.mlflow_admin_password
        username = var.mlflow_admin_username
      }
      teams = [
        for k, v in local.teams : k
        if v.includes.MLFLOW
      ]
    }
  }

  rds = {
    db_name = module.rds.postgres.db_name
    host    = module.rds.postgres.host
    port    = module.rds.postgres.port
    users = {
      mlflow = {
        password = var.mlflow_postgresql_password
        username = var.mlflow_postgresql_username
      }
    }
  }

  s3 = {
    buckets = {
      mlflow = {
        arn  = module.s3.buckets.mlflow.arn
        name = module.s3.buckets.mlflow.name
      }
    }
    url = {
      egress = local.s3_egress_url
    }
  }

  depends_on = [
    module.iam,
    module.elb,
    module.rds,
    module.s3
  ]
}

module "service_resources" {
  source = "modules/service_resources"

  iam    = {
    users = {
      admin = {
        region = module.iam.users.admin.region
      }
      teams = {
        for k, team in local.teams : k => {
          password = module.iam.users.teams[k].password
          username = module.iam.users.teams[k].username
        }
      }
    }
  }

  ecr    = {
    aws = {
      endpoint = local.ecr_aws_endpoint
      token = {
        authorization_token = local.ecr_authorization_token
        password = local.ecr_password
        username = local.ecr_username
      }
    }
  }

  eks = {
    users = {
      teams = {
        for k, v in module.eks.cluster : k => {
          kubernetes = {
            namespace = v.users.teams[k].kubernetes.namespace
          }
        }
      }
    }
  }

  mlflow = {
    url = {
      egress = module.mlflow.mlflow_internal_url
      internal = module.mlflow.mlflow_ingress_url
    }
    users = {
      teams = {
        for k, v in module.mlflow.mlflow_team_workspaces : k => {
          password = v.password
          username = v.username
        }
      }
    }
  }

  mwaa   = {
    url = {
      egress = module.mwaa.url.egress
    }
    users = {
      teams = {
        for k, v in module.mwaa.users.teams : k => {
          environment = {
            name = v.environment.name
          }
          connections = {
            prefix = v.connections.prefix
          }
          variables = {
            prefix = v.variables.prefix
          }
        }
      }
    }
  }

  rds    = {
    postgres = {
      host = module.rds.postgres.host
      port = module.rds.postgres.port
      db_name = module.rds.postgres.db_name
      users = {
        teams = {
          for k, v in module.postgresql.users.teams : k => {
            password = v.password
            username = v.username
          }
        }
      }
    }
  }

  s3 = {
    users = {
      teams = [
        for k, v in local.teams : k
        if v.includes.S3
      ]
    }
  }

  depends_on = [
    module.iam
  ]
}