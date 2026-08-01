output "aws_ecr_repository_urls"  { value = module.ecr_repository.repository_urls }
output "aws_eks_cluster_name"     { value = module.eks_cluster.name }
output "aws_eks_cluster_endpoint" { value = module.eks_cluster.endpoint }
output "aws_eks_oidc_issuer_url"  { value = module.eks_cluster.oidc_issuer_url }  # NEW

output "aws_mwaa_environment_name"          { value = module.aws_mwaa_environment.name }
output "aws_mwaa_environment_webserver_url" { value = module.aws_mwaa_environment.webserver_url }

output "aws_rds_db_identifier" { value = module.rds_db.identifier }
output "aws_rds_db_address"    { value = module.rds_db.address }

output "aws_s3_mlflow_bucket_name" { value = module.s3.mlflow_bucket_name }
output "aws_s3_mle_bucket_name"    { value = module.s3.mwaa_bucket_name }
output "aws_s3_team_bucket_names"  { value = module.s3.team_bucket_names }          # NEW

output "aws_iam_oidc_provider_arn" { value = module.aws_iam_oidc.oidc_provider_arn } # NEW
output "aws_iam_team_role_arns"    { value = module.aws_iam_oidc.team_role_arns }     # NEW

output "aws_secrets_manager_team_policy_arns" {                                       # NEW
  value = module.secrets_manager.team_secrets_policy_arns
}

output "mlflow_tracking_uri" { value = module.helm_apps.mlflow_tracking_uri }

output "postgresql_team_usernames" {                                                   # NEW (replaces per-field outputs)
  value     = module.postgresql.team_usernames
  sensitive = true
}
output "postgresql_team_passwords" {                                                   # NEW
  value     = module.postgresql.team_passwords
  sensitive = true
}

output "kubernetes_team_namespaces"    { value = module.kubernetes_resources.team_namespaces }    # NEW
output "kubernetes_shared_configmap"   { value = module.kubernetes_resources.shared_configmap_name } # NEW