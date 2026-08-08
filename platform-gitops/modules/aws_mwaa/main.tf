# EKS AUTHENTICATION
resource "aws_s3_object" "upload_kubeconfig_for_mwaa" {
  bucket = local.s3.buckets.mwaa.name
  key    = "${local.s3_dags.path}/${local.s3_kubeconfig_file_path_for_mwaa}"
  source = local.local_files.kubeconfig.host.file.path
  etag   = filemd5(local.local_files.kubeconfig.host.file.path)
}
# MWAA
resource "aws_iam_role_policy" "mwaa" {
  role = local.mwaa.role.arn
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
        Resource = local.s3.buckets.mwaa.arn
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:PutObject"
        ],
        Resource = "${local.s3.buckets.mwaa.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "${local.secretsmanager_airflow.connections.arn}/*",
          "${local.secretsmanager_airflow.variables.arn}/*"
        ]
      }
    ]
  })
}
resource "aws_mwaa_environment" "mwaa" {
  name               = "mwaa"
  airflow_version    = "2.10.3"
  execution_role_arn = local.mwaa.role.arn
  source_bucket_arn  = local.s3.buckets.mwaa.arn
  dag_s3_path        = local.s3_dags.path

  airflow_configuration_options = {
    "secrets.backend" = "airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend"
    "secrets.backend_kwargs" = jsonencode({
      connections_prefix = local.airflow_secrets_backend.connections.prefix
      variables_prefix   = local.airflow_secrets_backend.variables.prefix
      sep                = "/"
      endpoint_url       = local.secretsmanager.container.endpoint_url
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
  for_each = local.aws.users.teams
  role     = each.value.role.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = local.s3.buckets.mwaa.arn
        Condition = {
          StringLike = {
            "s3:prefix" = [
              "${local.s3_dags.path}/${each.key}",
              "${local.s3_dags.path}/${each.key}/*"
            ]
          }
        }
      },
      {
        Effect = "Allow"
        Action = "s3:*"
        Resource = [
          "${local.s3_dags.arn}/${each.key}",
          "${local.s3_dags.arn}/${each.key}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = "secretsmanager:*"
        Resource = [
          "${local.secretsmanager_airflow.connections.arn}/${each.key}-*",
          "${local.secretsmanager_airflow.connections.arn}/${each.key}/*",
          "${local.secretsmanager_airflow.variables.arn}/${each.key}-*",
          "${local.secretsmanager_airflow.variables.arn}/${each.key}/*"
        ]
      },
    ]
  })
}