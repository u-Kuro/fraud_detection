locals {
  dag_s3_path_name = "dags"
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
      "-s3_dag_kubeconfig_uri 's3://${var.s3_mwaa_bucket_name}/${local.dag_s3_path_name}/kubeconfig.yaml'"
    ])
  }
}

resource "aws_iam_role" "mwaa" {
  name = "mwaa_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = {
        Service = [
          "airflow.amazonaws.com",
          "airflow-env.amazonaws.com"
        ]
      }
      Action = "sts:AssumeRole"
    }]
  })
}
locals {
  airflow_secrets_connections_prefix = "airflow/connections"
  airflow_secrets_variables_prefix   = "airflow/variables"
}
resource "aws_iam_role_policy" "mwaa" {
  name = "mwaa_role_policy"
  role = aws_iam_role.mwaa.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          var.s3_mwaa_bucket_arn,
          "${var.s3_mwaa_bucket_arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = [
          "arn:aws:secretsmanager:*:${var.aws_account_id}:secret:${local.airflow_secrets_connections_prefix}/*",
          "arn:aws:secretsmanager:*:${var.aws_account_id}:secret:${local.airflow_secrets_variables_prefix}/*",
        ]
      }
    ]
  })
}

resource "aws_mwaa_environment" "mwaa" {
  name               = "mwaa"
  airflow_version    = "2.10.3"
  execution_role_arn = aws_iam_role.mwaa.arn
  source_bucket_arn  = var.s3_mwaa_bucket_arn
  dag_s3_path        = "${var.s3_mwaa_bucket_name}/${local.dag_s3_path_name}"

  airflow_configuration_options = {
    "secrets.backend"         = "airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend"
    "secrets.backend_kwargs"  = jsonencode({
      connections_prefix = local.airflow_secrets_connections_prefix
      variables_prefix   = local.airflow_secrets_variables_prefix
      sep                = "/"
      endpoint_url       = var.secretsmanager_service_endpoint_url
    })
  }

  network_configuration {
    security_group_ids  = ["sg-00000000000000001"]
    subnet_ids          = ["subnet-00000000000000001", "subnet-00000000000000002"]
  }
}

resource "aws_iam_user_policy" "teams" {
  for_each = var.teams
  name     = "${each.key}_mwaa_policy"
  user     = each.value.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid     = "S3OwnDAGs"
        Effect  = "Allow"
        Action  = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.s3_mwaa_bucket_arn,
          "${var.s3_mwaa_bucket_arn}/${local.dag_s3_path_name}/${each.key}/*"
        ]
        Condition = {
          StringLike = {
            "s3:prefix" = ["${local.dag_s3_path_name}/${each.key}/*"]
          }
        }
      },
      {
        Sid     = "SMOwnConnections"
        Effect  = "Allow"
        Action  = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:CreateSecret",
          "secretsmanager:PutSecretValue",
          "secretsmanager:DeleteSecret"
        ]
        Resource = ["arn:aws:secretsmanager:*:${var.aws_account_id}:secret:${local.airflow_secrets_connections_prefix}/${each.key}/*"]
      },
      {
        Sid     = "SMOwnVariables"
        Effect  = "Allow"
        Action  = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:CreateSecret",
          "secretsmanager:PutSecretValue",
          "secretsmanager:DeleteSecret"
        ]
        Resource = ["arn:aws:secretsmanager:*:${var.aws_account_id}:secret:${local.airflow_secrets_variables_prefix}/${each.key}/*"]
      },
    ]
  })
}