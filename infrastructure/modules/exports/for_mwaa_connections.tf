# Kubernetes
# /teams-connections
resource "aws_secretsmanager_secret" "mwaa_teams_k8s_connections" {
  for_each = var.mwaa_teams
  name     = "${var.mwaa_teams_connections_prefixes[each.key]}/${local.mwaa_connections_k8s_connection_id}"

  depends_on = [
    kubernetes_namespace_v1.eks_teams
  ]
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_k8s_connections" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_k8s_connections
  secret_id = each.value.id

  secret_string = jsonencode({
    conn_type = "kubernetes",
    extra = {
      kube_config_path = var.mwaa_teams_kubeconfig_file_paths[each.key] # /opt/airflow/kubeconfig.yaml
      namespace        = var.eks_teams_namespaces[each.key]
      in_cluster       = false
    }
  })

  depends_on = [
    aws_secretsmanager_secret.mwaa_teams_k8s_connections
  ]
}
# /teams-connection-id-variables
resource "aws_secretsmanager_secret" "mwaa_teams_k8s_connection_id_variables" {
  for_each = aws_secretsmanager_secret.mwaa_teams_k8s_connections
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_k8s_connection_id_name}"

  depends_on = [aws_secretsmanager_secret.mwaa_teams_k8s_connections]
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_k8s_connection_id_variables" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_k8s_connection_id_variables
  secret_id = each.value.id

  secret_string = local.mwaa_connections_k8s_connection_id

  depends_on = [
    aws_secretsmanager_secret.mwaa_teams_k8s_connections,
    aws_secretsmanager_secret.mwaa_teams_k8s_connection_id_variables
  ]
}
# Postgres
# /teams-connection
resource "aws_secretsmanager_secret" "mwaa_teams_postgres_connections" {
  for_each = var.rds_postgres_teams
  name     = "${var.mwaa_teams_connections_prefixes[each.key]}/${local.mwaa_connections_postgres_connection_id}"
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_postgres_connections" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_postgres_connections
  secret_id = each.value.id

  secret_string = jsonencode({
    conn_type = "postgres",
    host      = var.rds_postgres_host,
    port      = var.rds_postgres_port,
    login     = var.rds_postgres_teams_usernames[each.key],
    password  = var.rds_postgres_teams_passwords[each.key],
    schema    = var.rds_postgres_db_name
  })

  depends_on = [aws_secretsmanager_secret.mwaa_teams_postgres_connections]
}
# /teams-connection-id-variable
resource "aws_secretsmanager_secret" "mwaa_teams_postgres_connection_id_variables" {
  for_each = aws_secretsmanager_secret.mwaa_teams_postgres_connections
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_postgres_connection_id_name}"

  depends_on = [aws_secretsmanager_secret.mwaa_teams_postgres_connections]
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_postgres_connection_id_variables" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_postgres_connection_id_variables
  secret_id = each.value.id

  secret_string = local.mwaa_connections_postgres_connection_id

  depends_on = [
    aws_secretsmanager_secret.mwaa_teams_postgres_connections,
    aws_secretsmanager_secret.mwaa_teams_postgres_connection_id_variables
  ]
}
# S3
# /teams-connection
resource "aws_secretsmanager_secret" "mwaa_teams_s3_connections" {
  for_each = var.s3_teams
  name     = "${var.mwaa_teams_connections_prefixes[each.key]}/${local.mwaa_connections_s3_connection_id}"
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_s3_connections" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_s3_connections
  secret_id = each.value.id

  secret_string = jsonencode({
    conn_type = "aws",
    login     = var.iam_teams_usernames[each.key],
    password  = var.iam_teams_passwords[each.key],
    extra = {
      region_name = var.iam_admin_region
    }
  })

  depends_on = [aws_secretsmanager_secret.mwaa_teams_s3_connections]
}
# /teams-connection-id-variable
resource "aws_secretsmanager_secret" "mwaa_teams_s3_connection_id_variables" {
  for_each = aws_secretsmanager_secret.mwaa_teams_s3_connections
  name     = "${var.mwaa_teams_variables_prefixes[each.key]}/${local.mwaa_variables_s3_connection_id_name}"

  depends_on = [aws_secretsmanager_secret.mwaa_teams_s3_connections]
}
resource "aws_secretsmanager_secret_version" "mwaa_teams_s3_connection_id_variables" {
  for_each  = aws_secretsmanager_secret.mwaa_teams_s3_connection_id_variables
  secret_id = each.value.id

  secret_string = local.mwaa_connections_s3_connection_id

  depends_on = [
    aws_secretsmanager_secret.mwaa_teams_s3_connections,
    aws_secretsmanager_secret.mwaa_teams_s3_connection_id_variables
  ]
}