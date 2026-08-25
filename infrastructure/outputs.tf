# EKS
# /cluster
output "aws_eks_cluster_name" { value = module.eks.cluster_name }

# MLflow
# /urls
output "mlflow_host_url" { value = module.mlflow.host_url }

# MWAA
# /environment
output "mwaa_teams_environment_names" { value = module.mwaa.teams_environment_names }
# /urls
output "mwaa_host_url" { value = module.mwaa.host_url }

# RDS
# /postgres
output "aws_rds_postgres_identifier" { value = module.rds.postgres_identifier }
output "postgres_local_host" { value = module.rds.postgres_local_host }
output "postgres_local_port" { value = module.rds.postgres_local_port }
output "postgres_db_name" { value = module.rds.postgres_db_name }