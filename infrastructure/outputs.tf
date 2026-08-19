output "aws_eks_cluster_name" {
  value = module.eks.cluster_name
}
output "aws_eks_host_url" {
  value = module.eks.host_url
}

output "aws_rds_db_identifier" {
  value = module.rds.postgres_identifier
}
output "aws_rds_db_host" {
  value = module.rds.postgres_local_host
}
output "aws_rds_db_port" {
  value = module.rds.postgres_local_port
}

output "aws_s3_mlflow_bucket_name" {
  value = module.s3.mlflow_bucket_name
}

output "mlflow_tracking_uri" {
  value = module.mlflow.host_url
}

output "postgresql_mlflow_username" {
  value     = module.postgres.mlflow_username
  sensitive = true
}
output "postgresql_mlflow_password" {
  value     = module.postgres.mlflow_password
  sensitive = true
}