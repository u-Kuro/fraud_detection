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

output "secrets_manager_mle_pipeline_arn" {
  value = module.secrets_manager.mle_pipeline_secret_arn
}
output "secrets_manager_mle_fraud_detection_arn" {
  value = module.secrets_manager.mle_fraud_detection_secret_arn
}