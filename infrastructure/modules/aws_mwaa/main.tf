# Set Python package requirements for MWAA environments (not working with current setup)
resource "aws_s3_object" "upload_requirements_for_mwaa" {
  for_each = var.mwaa_teams
  bucket   = var.s3_teams_mwaa_bucket_names[each.key]
  key      = var.s3_teams_mwaa_requirements_file_path
  source   = var.local_files_mwaa_requirements_file_path
  etag     = filemd5(var.local_files_mwaa_requirements_file_path)
}
# Upload K8s cluster credential file in MWAA environments for authentication (not working with current setup)
resource "aws_s3_object" "upload_kubeconfig_for_mwaa" {
  for_each = var.mwaa_teams
  bucket   = var.s3_teams_mwaa_bucket_names[each.key]
  key      = "${var.s3_teams_mwaa_dag_path}/${var.s3_teams_mwaa_kubeconfig_file_path}"
  source   = var.local_files_kubeconfig_for_docker_file_path
  etag     = filemd5(var.local_files_kubeconfig_for_docker_file_path)
}
# Create MWAA environments for each team
resource "aws_mwaa_environment" "teams" {
  for_each           = var.mwaa_teams
  name               = local.mwaa_teams_environment_names[each.key]
  airflow_version    = local.mwaa_airflow_version
  execution_role_arn = var.iam_teams_role_arns[each.key]

  source_bucket_arn    = var.s3_teams_mwaa_bucket_arns[each.key]
  requirements_s3_path = var.s3_teams_mwaa_requirements_file_path
  dag_s3_path          = local.mwaa_teams_environment_dag_s3_paths[each.key]

  airflow_configuration_options = {
    "secrets.backend" = "airflow.providers.amazon.aws.secrets.secrets_manager.SecretsManagerBackend"
    "secrets.backend_kwargs" = jsonencode({
      connections_prefix = local.mwaa_teams_airflow_secrets_backend_connections_prefixes[each.key]
      variables_prefix   = local.mwaa_teams_airflow_secrets_backend_variables_prefixes[each.key]
      sep                = "/"
      endpoint_url       = var.secrets_manager_url # "http://ministack:4566
      profile_name       = local.mwaa_secrets_backend_aws_profile_name
    })
  }

  network_configuration {
    security_group_ids = ["sg-00000000000000000", "sg-00000000000000001"]
    subnet_ids         = ["subnet-00000000000000000", "subnet-00000000000000001"]
  }

  depends_on = [
    # Needs initial files for environment
    aws_s3_object.upload_requirements_for_mwaa,
    aws_s3_object.upload_kubeconfig_for_mwaa,
  ]
}
# Allow teams to manage attached repositories in their MWAA environments
resource "aws_iam_user_policy" "teams" {
  for_each = var.mwaa_teams
  user     = var.iam_teams_names[each.key]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "secretsmanager:*"
        Resource = [
          # connections
          "${local.secrets_manager_mwaa_teams_airflow_secrets_backend_connections_arns[each.key]}/",
          "${local.secrets_manager_mwaa_teams_airflow_secrets_backend_connections_arns[each.key]}/*",
          # variables
          "${local.secrets_manager_mwaa_teams_airflow_secrets_backend_variables_arns[each.key]}/",
          "${local.secrets_manager_mwaa_teams_airflow_secrets_backend_variables_arns[each.key]}/*",
        ]
      },
      {
        Effect = "Deny"
        Action = [
          "s3:DeleteObject",
          "s3:DeleteObjectVersion"
        ]
        Resource = [
          aws_s3_object.upload_requirements_for_mwaa[each.key].arn,
          aws_s3_object.upload_kubeconfig_for_mwaa[each.key].arn
        ]
      }
    ]
  })

  depends_on = [
    # Needs proper environment before giving access to its resources
    aws_mwaa_environment.teams[each.key]
  ]
}
# Setup and get Ministack's EKS configurations
data "external" "airflow_configuration" {
  for_each = aws_mwaa_environment.teams

  program = ["powershell", "-File", "${path.module}/scripts/setup-and-get-airflow-configurations.ps1"]

  query = {
    ministack_network_name                 = var.ministack_network_name
    airflow_container_url                  = local.mwaa_urls[each.key] # https://172.19.0.5:[8080|internal-port]
    airflow_requirements_file_path         = var.local_files_mwaa_requirements_file_path
    airflow_python_packages_constraint_url = local.mwaa_airflow_python_packages_constraint_url
    kubeconfig_for_docker_file_path        = var.local_files_kubeconfig_for_docker_file_path
    secrets_manager_url                    = var.secrets_manager_url # "http://ministack:4566
    iam_admin_region                       = var.iam_admin_region
    aws_access_key_id                      = var.iam_teams_usernames[each.key]
    aws_secret_access_key                  = var.iam_teams_passwords[each.key]
  }
}
# {
#    "Environment": {
#        "Name": "test",
#        "Status": "AVAILABLE",
#        "Arn": "arn:aws:airflow:us-east-1:000000000000:environment/test",
#        "CreatedAt": "2026-08-19T15:16:06.087223+08:00",
#        "WebserverUrl": "172.19.0.5:8080",
#        "ExecutionRoleArn": "arn:aws:iam::000000000000:role/mwaa-role-test",
#        "ServiceRoleArn": "arn:aws:iam::000000000000:role/aws-service-role/airflow.amazonaws.com/AWSServiceRoleForAmazonMWAA",
#        "AirflowVersion": "3.0.6",
#        "SourceBucketArn": "arn:aws:s3:::airflow-dags-test",
#        "DagS3Path": "dags/",
#        "AirflowConfigurationOptions": {},
#        "EnvironmentClass": "mw1.small",
#        "MaxWorkers": 5,
#        "NetworkConfiguration": {
#            "SubnetIds": [
#                "0",
#                "1"
#            ],
#            "SecurityGroupIds": [
#                "0"
#            ]
#        },
#        "LoggingConfiguration": {},
#        "LastUpdate": {
#            "Status": "SUCCESS"
#        },
#        "Tags": {},
#        "WebserverAccessMode": "PUBLIC_ONLY",
#        "MinWorkers": 1,
#        "Schedulers": 2,
#        "MinWebservers": 2,
#        "MaxWebservers": 2
#    }
#}