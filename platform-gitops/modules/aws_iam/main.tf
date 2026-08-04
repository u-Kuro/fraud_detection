# ADMIN
data "aws_caller_identity" "admin" {}
resource "aws_iam_role" "admin" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect  = "Allow"
      Action  = "sts:AssumeRole"
      Principal = {
        AWS = data.aws_caller_identity.admin.arn
      }
    }]
  })
}
resource "aws_iam_role_policy_attachment" "admin" {
  role       = aws_iam_role.admin.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
# TEAMS
resource "aws_iam_group" "teams" {
  for_each  = var.teams
  name      = each.value
}
resource "aws_iam_access_key" "teams" {
  for_each = aws_iam_group.teams
  user     = each.value.name
}
resource "aws_iam_role" "teams" {
  for_each = aws_iam_group.teams
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect  = "Allow"
      Action  = "sts:AssumeRole"
      Principal = {
        AWS = each.value.arn
      }
    }]
  })
}
# SERVICES
resource "aws_iam_role" "ec2" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect  = "Allow"
      Action  = "sts:AssumeRole"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
}
resource "aws_iam_role" "eks" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect  = "Allow"
      Action  = "sts:AssumeRole"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}
resource "aws_iam_role" "mwaa" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect  = "Allow"
        Action  = "sts:AssumeRole"
        Principal = {
          Service = "airflow.amazonaws.com"
        }
      },
      {
        Effect  = "Allow"
        Action  = "sts:AssumeRole"
        Principal = {
          Service = "airflow-env.amazonaws.com"
        }
      }
    ]
  })
}
resource "aws_iam_role" "rds" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect  = "Allow"
      Action  = "sts:AssumeRole"
      Principal = {
        Service = "rds.amazonaws.com"
      }
    }]
  })
}