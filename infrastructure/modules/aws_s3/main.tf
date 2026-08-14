# Create bucket for RDS Postgres
resource "aws_s3_bucket" "postgres" {
  bucket        = "Postgres"
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "postgres" {
  bucket = aws_s3_bucket.postgres.id

  versioning_configuration {
    status = "Enabled"
  }

  depends_on = [aws_s3_bucket.postgres]
}
resource "aws_s3_bucket_public_access_block" "postgres" {
  bucket                  = aws_s3_bucket.postgres.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  depends_on = [aws_s3_bucket.postgres]
}
# Create bucket for MLflow
resource "aws_s3_bucket" "mlflow" {
  bucket        = "MLflow"
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "mlflow" {
  bucket = aws_s3_bucket.mlflow.id

  versioning_configuration {
    status = "Enabled"
  }

  depends_on = [aws_s3_bucket.mlflow]
}
resource "aws_s3_bucket_public_access_block" "mlflow" {
  bucket                  = aws_s3_bucket.mlflow.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  depends_on = [aws_s3_bucket.mlflow]
}
# Create buckets for each team
resource "aws_s3_bucket" "teams" {
  for_each      = var.s3_teams
  bucket        = each.value
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "teams" {
  for_each = aws_s3_bucket.teams
  bucket   = each.value.id

  versioning_configuration {
    status = "Enabled"
  }

  depends_on = [aws_s3_bucket.teams]
}
resource "aws_s3_bucket_public_access_block" "teams" {
  for_each                = aws_s3_bucket.teams
  bucket                  = each.value.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  depends_on = [aws_s3_bucket.teams]
}
# Allow teams to manage their own bucket
resource "aws_iam_user_policy" "teams" {
  for_each = aws_s3_bucket.teams
  user     = var.iam_teams_names[each.key]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "s3:*"
        Resource = [
          each.value.arn,
          "${each.value.arn}/*"
        ]
      },
      {
        Effect = "Deny"
        Action = [
          "s3:DeleteBucket"
        ]
        Resource = each.value.arn
      }
    ]
  })

  depends_on = [aws_s3_bucket.teams]
}
# Create buckets for each team with MWAA
resource "aws_s3_bucket" "teams_mwaa" {
  for_each      = var.mwaa_teams
  bucket        = "${each.key}_MWAA"
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "teams_mwaa" {
  for_each = aws_s3_bucket.teams_mwaa
  bucket   = each.value.id

  versioning_configuration {
    status = "Enabled"
  }

  depends_on = [aws_s3_bucket.teams_mwaa]
}
# Allow teams to manage their own buckets used in MWAA
resource "aws_iam_user_policy" "teams_mwaa" {
  for_each = aws_s3_bucket.teams_mwaa
  user     = var.iam_teams_names[each.key]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "s3:*"
        Resource = [
          each.value.arn,
          "${each.value.arn}/*"
        ]
      },
      {
        Effect = "Deny"
        Action = [
          "s3:DeleteBucket"
        ]
        Resource = each.value.arn
      }
    ]
  })

  depends_on = [aws_s3_bucket.teams_mwaa]
}