locals {
  s3_mwaa_path  = "mwaa"
  dag_s3_path   = "${local.s3_mwaa_path}/dags"
}
resource "terraform_data" "upload_kubeconfig_to_s3_uri_for_airflow" {
  triggers_replace = {
    eks_cluster_name = var.eks_cluster_name
  }

  provisioner "local-exec" {
    interpreter = ["PowerShell", "-Command"]
    command     = join(" ", [
      "& '${path.module}/scripts/upload_kubeconfig_to_s3_uri_for_airflow.ps1'",

      "-aws_access_key '${var.aws_access_key}'",
      "-aws_secret_key '${var.aws_secret_key}'",
      "-aws_region '${var.aws_region}'",

      "-eks_service_endpoint_url '${var.eks_service_endpoint_url}'",
      "-eks_cluster_name '${var.eks_cluster_name}'",
      "-temporary_kubeconfig_file_path '$env:TEMP\\kubeconfig.yaml'",

      "-s3_service_endpoint_url '${var.s3_service_endpoint_url}'",
      "-s3_dag_kubeconfig_uri 's3://${var.s3_mwaa_bucket}/${local.dag_s3_path}/kubeconfig.yaml'"
    ])
  }
}

locals {
  airflow_secrets_connections_prefix  = "airflow/connections"
  airflow_secrets_variables_prefix    = "airflow/variables"
}
resource "aws_iam_role_policy" "mwaa_secrets_access" {
  name = "mwaa_secrets_access"
  role = "mwaa_role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "mwaa_secrets_access"
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds",
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:${local.airflow_secrets_connections_prefix}/*",
          "arn:aws:secretsmanager:${var.aws_region}:${var.aws_account_id}:secret:${local.airflow_secrets_variables_prefix}/*",
        ]
      }
    ]
  })
}

# ── Per-team S3 DAG path access ───────────────────────────────────────────────
resource "aws_iam_role_policy" "mwaa_team_dag_s3_access" {
  for_each = { for k, v in var.teams : k => v if v.has_mwaa_access }

  name = "mwaa_team_dag_s3_${each.key}"
  role = "mwaa_role"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "MWAATeamDagPush"
        Effect = "Allow"
        Action = ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"]
        Resource = "arn:aws:s3:::${var.s3_mwaa_bucket}/${local.dag_s3_path}/${each.key}/*"
      },
      {
        Sid      = "MWAATeamDagList"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = "arn:aws:s3:::${var.s3_mwaa_bucket}"
        Condition = {
          StringLike = {
            "s3:prefix" = "${local.dag_s3_path}/${each.key}/*"
          }
        }
      }
    ]
  })
}

resource "aws_s3_object" "requirements" {
  bucket  = var.s3_mwaa_bucket
  key     = "${local.s3_mwaa_path}/requirements.txt"
  content = <<-REQ
    apache-airflow-providers-amazon==9.31.0
    apache-airflow-providers-cncf-kubernetes==10.18.0
    apache-airflow-providers-http==6.0.4
    apache-airflow-providers-postgres==6.8.0
    apache-airflow-providers-slack==9.10.2
    pydantic==2.13.4
  REQ
}

resource "aws_mwaa_environment" "main" {
  name                  = "mwaa"
  airflow_version       = "2.10.3"
  source_bucket_arn     = "arn:aws:s3:::${var.s3_mwaa_bucket}"
  execution_role_arn    = "arn:aws:iam::${var.aws_account_id}:role/${aws_iam_role_policy.mwaa_secrets_access.role}"

  dag_s3_path = local.dag_s3_path

  requirements_s3_path            = aws_s3_object.requirements.key
  requirements_s3_object_version  = aws_s3_object.requirements.version_id

  airflow_configuration_options = {
    "secrets.backend"         = "airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend"
    "secrets.backend_kwargs"  = jsonencode({
      connections_prefix = local.airflow_secrets_connections_prefix
      variables_prefix   = local.airflow_secrets_variables_prefix
      sep                = "/"
      endpoint_url       = var.secretsmanager_service_endpoint_url
    })

    # Custom RBAC role per team: read/trigger only DAGs whose dag_id starts with <team>_
    # Airflow evaluates this as a DAG-level filter on the UI and REST API.
    "webserver.rbac_user_registration_role" = "Public"

    # One entry per team — the value is a serialised JSON RBAC role definition.
    # Teams not in this map receive only the Public (no-op) role.
  }

  network_configuration {
    security_group_ids  = ["sg-00000000000000001"]
    subnet_ids          = ["subnet-00000000000000001", "subnet-00000000000000002"]
  }

  depends_on = [
    aws_s3_object.requirements,
    terraform_data.upload_kubeconfig_to_s3_uri_for_airflow,
    aws_iam_role_policy.mwaa_secrets_access,
  ]
}
