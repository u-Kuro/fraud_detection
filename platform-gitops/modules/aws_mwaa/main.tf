# EKS AUTHENTICATION
locals {
  dag_s3_path_name          = "dags"
  kubeconfig_mwaa_file_path = "kubeconfig.yaml"
}
resource "aws_s3_object" "upload_kubeconfig_for_ministack_mwaa" {
  bucket = var.s3.mwaa_bucket.name
  # Path after dag_s3_path is the location in MWAA e.g. /usr/local/airflow/dags/[kubeconfig.yaml]
  key    = "${local.dag_s3_path_name}/${local.kubeconfig_mwaa_file_path}"
  source = var.kubeconfig.host.file.path
  etag   = filemd5(var.kubeconfig.host.file.path)
}
# MWAA
locals {
  airflow_secrets_connections_prefix = "airflow/connections"
  airflow_secrets_variables_prefix   = "airflow/variables"
}
resource "aws_iam_role_policy" "mwaa" {
  role = var.mwaa.role.arn
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:ListBucketVersions"
        ]
        Resource = var.s3.mwaa_bucket.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject"
        ],
        Resource = "${var.s3.mwaa_bucket.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:*:${var.aws_admin.accout_id}:secret:${local.airflow_secrets_connections_prefix}/*",
          "arn:aws:secretsmanager:*:${var.aws_admin.accout_id}:secret:${local.airflow_secrets_variables_prefix}/*"
        ]
      }
    ]
  })
}
resource "aws_mwaa_environment" "mwaa" {
  name               = "mwaa"
  airflow_version    = "2.10.3"
  execution_role_arn = var.mwaa.role.arn
  source_bucket_arn  = var.s3.mwaa_bucket.arn
  dag_s3_path        = local.dag_s3_path_name

  airflow_configuration_options = {
    "secrets.backend" = "airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend"
    "secrets.backend_kwargs" = jsonencode({
      connections_prefix = local.airflow_secrets_connections_prefix
      variables_prefix   = local.airflow_secrets_variables_prefix
      sep                = "/"
      endpoint_url       = var.secretsmanager.container.endpoint_url
    })
  }

  network_configuration {
    security_group_ids = ["sg-00000000000000001"]
    subnet_ids         = ["subnet-00000000000000001", "subnet-00000000000000002"]
  }

  depends_on = [aws_iam_role_policy.mwaa]
}
# TEAM PERMISSIONS
resource "aws_iam_role_policy" "teams" {
  for_each = var.teams
  role     = each.value.role.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = var.s3.mwaa_bucket.arn
        Condition = {
          StringLike = {
            "s3:prefix" = [
              "${local.dag_s3_path_name}/${each.key}",
              "${local.dag_s3_path_name}/${each.key}/*"
            ]
          }
        }
      },
      {
        Effect = "Allow"
        Action = "s3:*"
        Resource = [
          "${var.s3.mwaa_bucket.arn}/${local.dag_s3_path_name}/${each.key}",
          "${var.s3.mwaa_bucket.arn}/${local.dag_s3_path_name}/${each.key}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = "secretsmanager:*"
        Resource = [

          "arn:aws:secretsmanager:*:${var.aws_admin.accout_id}:secret:${local.airflow_secrets_connections_prefix}/${each.key}-*",
          "arn:aws:secretsmanager:*:${var.aws_admin.accout_id}:secret:${local.airflow_secrets_connections_prefix}/${each.key}/*",
          "arn:aws:secretsmanager:*:${var.aws_admin.accout_id}:secret:${local.airflow_secrets_variables_prefix}/${each.key}-*",
          "arn:aws:secretsmanager:*:${var.aws_admin.accout_id}:secret:${local.airflow_secrets_variables_prefix}/${each.key}/*"
        ]
      },
    ]
  })
}
