# INPUTS
locals {
  iam             = var.iam
  local_files     = var.local_files
  mwaa            = var.mwaa
  s3              = var.s3
  secrets_manager = var.secrets_manager
  ssm_parameter   = var.ssm_parameter
}
# COMPUTED
locals {
  # MWAA
  s3_mwaa_requirements_path = "requirements.txt"
  s3_mwaa_dag_path          = "DAG"
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
  _secrets_manager_base_arn_ = "arn:aws:secretsmanager:*:${local.iam.users.admin.account_id}:secret"
  secrets_manager_airflow = {
    connections = {
      arn = "${local._secrets_manager_base_arn_}:${local.airflow_secrets_backend.connections.prefix}"
    }
    variables = {
      arn = "${local._secrets_manager_base_arn_}:${local.airflow_secrets_backend.variables.prefix}"
    }
  }
}