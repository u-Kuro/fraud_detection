output "team_access_keys" {
  value     = module.iam.team_access_keys
  sensitive = true
}
output "mlflow_access_key" {
  value     = module.iam.mlflow_access_key
  sensitive = true
}

output "aws_ecr_repository_urls" {
  value = module.ecr.team_repository_urls
}

output "aws_eks_cluster_name" {
  value = module.eks.name
}
output "aws_eks_cluster_endpoint" {
  value = module.eks.endpoint
}
output "aws_eks_ecr_secret" {
  value = module.eks.ecr_secret_name
}

output "aws_mwaa_environment_name" {
  value = module.mwaa.name
}
output "aws_mwaa_environment_webserver_url" {
  value = module.mwaa.webserver_url
}

output "aws_rds_db_identifier" {
  value = module.rds.identifier
}
output "aws_rds_db_address" {
  value = module.rds.address
}

output "aws_s3_mlflow_bucket_name" {
  value = module.s3.mlflow_bucket_name
}
output "aws_s3_mle_bucket_name" {
  value = module.s3.mwaa_bucket_name
}

output "mlflow_tracking_uri" {
  value = module.mlflow.mlflow_tracking_uri
}

output "postgresql_mlflow_username" {
  value     = module.postgresql.mlflow_username
  sensitive = true
}
output "postgresql_mlflow_password" {
  value     = module.postgresql.mlflow_password
  sensitive = true
}
output "teams_credentials" {
  value     = module.postgresql.teams_credentials
  sensitive = true
}
output "teams_migration_credentials" {
  value     = module.postgresql.teams_migration_credentials
  sensitive = true
}