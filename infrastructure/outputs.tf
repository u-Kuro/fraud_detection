# EKS
# /cluster
output "aws_eks_cluster_name" { value = module.eks.cluster_name }

# Ministack
# /urls
output "ministack_host_url" { value = module.ministack_container.host_url }

# MLflow
# /urls
output "mlflow_host_url" { value = module.mlflow.host_url }

# MWAA
# /environment
output "mwaa_teams_environment_names" { value = module.mwaa.teams_environment_names }
# /teams
output "mwaa_teams_host_urls" { value = module.mwaa.teams_host_url }

# RDS
# /postgres
output "aws_rds_postgres_identifier" { value = module.rds.postgres_identifier }
output "postgres_local_host" { value = module.rds.postgres_local_host }
output "postgres_local_port" { value = module.rds.postgres_local_port }
output "postgres_db_name" { value = module.rds.postgres_db_name }