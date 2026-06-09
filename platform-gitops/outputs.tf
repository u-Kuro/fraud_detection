output "aws_ecr_name" {
  value = module.ecr_repository.name
}
output "aws_ecr_repository_url" {
  value = module.ecr_repository.repository_url
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

output "aws_s3_dags_bucket_name" {
  value = module.s3.dags_bucket_name
}
output "aws_s3_mlflow_bucket_name" {
  value = module.s3.mlflow_bucket_name
}

output "aws_mwaa_environment_webserver_url" {
  value = module.aws_mwaa_environment.webserver_url
}
