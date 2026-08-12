# RDS
resource "aws_s3_bucket" "rds" {
  bucket        = "RDS"
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "rds" {
  bucket = aws_s3_bucket.rds.id

  versioning_configuration {
    status = "Enabled"
  }

  depends_on = [aws_s3_bucket.rds]
}
resource "aws_s3_bucket_public_access_block" "rds" {
  bucket                  = aws_s3_bucket.rds.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  depends_on = [aws_s3_bucket.rds]
}
# MLFLOW
resource "aws_s3_bucket" "mlflow" {
  bucket        = "MLFLOW"
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
# TEAMS
resource "aws_s3_bucket" "teams" {
  for_each      = local.s3.users.teams
  bucket        = each.key
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
# TEAMS' PERMISSIONS
resource "aws_iam_role_policy" "teams" {
  for_each = local.s3.users.teams
  role     = local.iam.users.teams[each.key].role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "s3:*"
        Resource = [
          aws_s3_bucket.teams[each.key].arn,
          "${aws_s3_bucket.teams[each.key].arn}/*"
        ]
      },
      {
        Effect = "Deny"
        Action = [
          "s3:DeleteBucket"
        ]
        Resource = aws_s3_bucket.teams[each.key].arn
      }
    ]
  })

  depends_on = [aws_s3_bucket.teams]
}
# TEAMS' MWAA
resource "aws_s3_bucket" "teams_mwaa" {
  for_each      = local.mwaa.users.teams
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
# TEAMS' MWAA PERMISSIONS
resource "aws_iam_role_policy" "teams_mwaa" {
  for_each = local.mwaa.users.teams
  role     = local.iam.users.teams[each.key].role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "s3:*"
        Resource = [
          aws_s3_bucket.teams_mwaa[each.key].arn,
          "${aws_s3_bucket.teams_mwaa[each.key].arn}/*"
        ]
      },
      {
        Effect = "Deny"
        Action = [
          "s3:DeleteBucket"
        ]
        Resource = aws_s3_bucket.teams_mwaa[each.key].arn
      }
    ]
  })

  depends_on = [aws_s3_bucket.teams_mwaa]
}