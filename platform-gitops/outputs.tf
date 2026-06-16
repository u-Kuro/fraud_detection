output "aws_ecr_names" {
  value = module.ecr_repository.repository_names
}
output "aws_ecr_repository_urls" {
  value = module.ecr_repository.repository_urls
}

output "aws_eks_cluster_name" {
  value = module.eks_cluster.name
}
output "aws_eks_cluster_endpoint" {
  value = module.eks_cluster.endpoint
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
  value = module.s3.mle_bucket_name
}

output "aws_mwaa_environment_webserver_url" {
  value = module.aws_mwaa_environment.webserver_url
}

output "secrets_manager_mle_runtime_arn" {
  value = module.secrets_manager.mle_runtime_secret_arn
}
output "secrets_manager_fraud_api_arn" {
  value = module.secrets_manager.fraud_api_secret_arn
}