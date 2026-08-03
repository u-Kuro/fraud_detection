resource "aws_s3_bucket" "mwaa" {
  bucket        = "mwaa"
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "mwaa" {
  bucket = aws_s3_bucket.mwaa.id

  versioning_configuration {
    status = "Enabled"
  }

  depends_on = [aws_s3_bucket.mwaa]
}
resource "aws_s3_bucket_public_access_block" "mwaa" {
  bucket                  = aws_s3_bucket.mwaa.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  depends_on = [aws_s3_bucket.mwaa]
}

resource "aws_s3_bucket" "mlflow" {
  bucket        = "mlflow"
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

resource "aws_s3_bucket" "teams" {
  for_each      = var.teams
  bucket        = each.key
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "teams" {
  for_each  = aws_s3_bucket.teams
  bucket    = each.value.id

  versioning_configuration {
    status = "Enabled"
  }

  depends_on = [aws_s3_bucket.mlflow]
}
resource "aws_s3_bucket_public_access_block" "teams" {
  for_each                = aws_s3_bucket.teams
  bucket                  = each.value.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  depends_on = [aws_s3_bucket.mwaa]
}

resource "aws_iam_user_policy" "teams" {
  for_each = aws_s3_bucket.teams
  name     = "${each.key}_s3_policy"
  user     = var.teams[each.key].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3OwnTeamBucket"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          each.value.arn,
          "${each.value.arn}/*"
        ]
      }
    ]
  })
}