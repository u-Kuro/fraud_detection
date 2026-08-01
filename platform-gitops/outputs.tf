output "aws_ecr_repository_urls" {
  value = module.ecr_repository.repository_urls
}

output "aws_eks_cluster_name" {
  value = module.eks_cluster.name
}
output "aws_eks_cluster_endpoint" {
  value = module.eks_cluster.endpoint
}

output "aws_mwaa_environment_name" {
  value = module.aws_mwaa_environment.name
}
output "aws_mwaa_environment_webserver_url" {
  value = module.aws_mwaa_environment.webserver_url
}

output "aws_rds_db_identifier" {
  value = module.rds_db.identifier
}
output "aws_rds_db_address" {
  value = module.rds_db.address
}

output "aws_s3_mlflow_bucket_name" {
  value = module.s3.mlflow_bucket_name
}
output "aws_s3_mle_bucket_name" {
  value = module.s3.mwaa_bucket_name
}

output "aws_secrets_manager_mle_secrets_policy_arn" {
  value = module.secrets_manager.mle_secrets_policy_arn
}

output "mlflow_tracking_uri" {
  value = module.helm_apps.mlflow_tracking_uri
}

output "postgresql_mlflow_username" {
  value = module.postgresql.mlflow_username
  sensitive = true
}
output "postgresql_mlflow_password" {
  value = module.postgresql.mlflow_password
  sensitive = true
}
output "postgresql_mle_username" {
  value = module.postgresql.mle_username
  sensitive = true
}
output "postgresql_mle_password" {
  value = module.postgresql.mle_password
  sensitive = true
}
output "postgresql_mle_migration_username" {
  value = module.postgresql.mle_migration_username
  sensitive = true
}
output "postgresql_mle_migration_password" {
  value = module.postgresql.mle_migration_password
  sensitive = true
}