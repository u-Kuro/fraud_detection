# INPUTS
locals {
  aws            = var.aws
  local_files    = var.local_files
  mwaa           = var.mwaa
  s3             = var.s3
  secretsmanager = var.secretsmanager
}
# COMPUTED
locals {
  # DAGS
  s3_dags = {
    arn  = "${local.s3.buckets.mwaa.arn}/${local.s3_dags.path}"
    path = "dags"
  }
  # KUBECONFIG `/usr/local/airflow/dags/[s3_kubeconfig_file_path_for_mwaa]`
  s3_kubeconfig_file_path_for_mwaa = "kubeconfig.yaml"
  # AIRFLOW SECRETS MANAGER BACKEND
  airflow_secrets_backend = {
    connections = {
      prefix = "airflow/connections"
    }
    variables = {
      prefix = "airflow/variables"
    }
  }
  secretsmanager_airflow = {
    arn = "arn:aws:secretsmanager:*:${local.aws.users.admin.account_id}:secret"
    connections = {
      arn = "${local.secretsmanager_airflow.arn}:${local.airflow_secrets_backend.connections.prefix}"
    }
    variables = {
      arn = "${local.secretsmanager_airflow.arn}:${local.airflow_secrets_backend.variables.prefix}"
    }
  }
}