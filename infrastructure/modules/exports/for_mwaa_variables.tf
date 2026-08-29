# Kubernetes
# /teams-namespaces
resource "aws_secretsmanager_secret" "mwaa_teams_k8s_namespace_variables" {
  for_each = kubernetes_namespace_v1.eks_teams
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_namespace}"
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_k8s_namespace_variables" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_k8s_namespace_variables
  secret_id = each.value.id

  secret_string = var.eks_teams_namespaces[each.key]

  depends_on = [
    kubernetes_namespace_v1.eks_teams,
    aws_secretsmanager_secret.mwaa_teams_k8s_namespace_variables
  ]
}
# /teams-base-config-maps
resource "aws_secretsmanager_secret" "mwaa_teams_k8s_base_config_map_variables" {
  for_each = kubernetes_config_map_v1.eks_teams_base_config_map
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_base_config_map_name}"
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_k8s_base_config_map_variables" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_k8s_base_config_map_variables
  secret_id = each.value.id

  secret_string = local.eks_k8s_base_config_map_name

  depends_on = [
    kubernetes_config_map_v1.eks_teams_base_config_map,
    aws_secretsmanager_secret.mwaa_teams_k8s_base_config_map_variables
  ]
}
# /teams-base-secrets
resource "aws_secretsmanager_secret" "mwaa_teams_k8s_base_secret_variables" {
  for_each = kubernetes_secret_v1.eks_teams_base_secret
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_base_secret_name}"
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_k8s_base_secret_variables" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_k8s_base_secret_variables
  secret_id = each.value.id

  secret_string = local.eks_k8s_base_secret_name

  depends_on = [
    kubernetes_secret_v1.eks_teams_base_secret,
    aws_secretsmanager_secret.mwaa_teams_k8s_base_secret_variables
  ]
}
# /teams-docker-registries
resource "aws_secretsmanager_secret" "mwaa_teams_k8s_docker_registry_variables" {
  for_each = kubernetes_secret_v1.eks_teams_docker_registry
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_docker_registry_secret_name}"
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_k8s_docker_registry_variables" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_k8s_docker_registry_variables
  secret_id = each.value.id

  secret_string = local.eks_k8s_docker_registry_secret_name

  depends_on = [
    kubernetes_secret_v1.eks_teams_docker_registry,
    aws_secretsmanager_secret.mwaa_teams_k8s_docker_registry_variables
  ]
}
# MLflow
# /teams-urls
resource "aws_secretsmanager_secret" "mwaa_teams_mlflow_url_variables" {
  for_each = var.mlflow_teams
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_mlflow_tracking_uri}"
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_mlflow_url_variables" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_mlflow_url_variables
  secret_id = each.value.id

  secret_string = var.mlflow_ingress_url

  depends_on = [
    aws_secretsmanager_secret.mwaa_teams_mlflow_url_variables
  ]
}
# /teams-usernames
resource "aws_secretsmanager_secret" "mwaa_teams_mlflow_username_variables" {
  for_each = var.mlflow_teams
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_mlflow_tracking_username}"
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_mlflow_username_variables" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_mlflow_username_variables
  secret_id = each.value.id

  secret_string = var.mlflow_teams_usernames[each.key]

  depends_on = [
    aws_secretsmanager_secret.mwaa_teams_mlflow_username_variables
  ]
}
# /teams-passwords
resource "aws_secretsmanager_secret" "mwaa_teams_mlflow_password_variables" {
  for_each = var.mlflow_teams
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_mlflow_tracking_password}"
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_mlflow_password_variables" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_mlflow_password_variables
  secret_id = each.value.id

  secret_string = var.mlflow_teams_passwords[each.key]

  depends_on = [aws_secretsmanager_secret.mwaa_teams_mlflow_password_variables]
}