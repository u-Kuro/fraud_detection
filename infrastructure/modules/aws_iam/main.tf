# Initialize admin role
data "aws_caller_identity" "admin" {}
data "aws_region" "admin" {}
# Give full access to admin
resource "aws_iam_user_policy_attachment" "admin" {
  user       = split("/", data.aws_caller_identity.admin.arn)[1]
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
# Create IAM user per team
resource "aws_iam_user" "teams" {
  for_each = var.iam_teams
  name     = each.key
}
# Create AWS credentials per team
resource "aws_iam_access_key" "teams" {
  for_each = aws_iam_user.teams
  user     = each.value.name

  depends_on = [aws_iam_user.teams]
}
# Create roles for services
resource "aws_iam_role" "ec2" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRole"
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
      Effect = "Allow"
      Action = "sts:AssumeRole"
      Principal = {
        Service = "eks.amazonaws.com"
      }
    }]
  })
}
resource "aws_iam_role" "mwaa" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRole"
      Principal = {
        Service = [
          "airflow.amazonaws.com",
          "airflow-env.amazonaws.com"
        ]
      }
    }]
  })
}
resource "aws_iam_role" "rds" {
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = "sts:AssumeRole"
      Principal = {
        Service = "rds.amazonaws.com"
      }
    }]
  })
}