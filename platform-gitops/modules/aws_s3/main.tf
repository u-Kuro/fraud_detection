resource "aws_s3_bucket" "mwaa" {
  bucket        = "mwaa"
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "mwaa_bucket_versioning" {
  bucket = aws_s3_bucket.mwaa.id
  versioning_configuration { status = "Enabled" }
  depends_on = [aws_s3_bucket.mwaa]
}

resource "aws_s3_bucket" "mlflow" {
  bucket        = "mlflow"
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "mwaa_bucket_versioning" {
  bucket = aws_s3_bucket.mlflow.id
  versioning_configuration { status = "Enabled" }
  depends_on = [aws_s3_bucket.mlflow]
}

locals {
  # Teams that have their own dedicated S3 bucket
  s3_teams = ["mle"]
}
resource "aws_s3_bucket" "team_s3_buckets" {
  for_each      = local.s3_teams
  bucket        = each.value
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "team_s3_buckets_versioning" {
  for_each  = aws_s3_bucket.team_s3_buckets
  bucket    = each.value.id
  versioning_configuration { status = "Enabled" }
  depends_on = [aws_s3_bucket.mlflow]
}

# ── Team bucket IAM policy — full access to own bucket only ──────────────────
# MiniStack: simulated.
resource "aws_iam_role_policy" "team_s3_bucket_access" {
  for_each = aws_s3_bucket.team_s3_buckets

  name = "${each.value.id}_s3_bucket_access"
  role = var.team_role_names[each.key]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListOwnBucket"
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = "arn:aws:s3:::${each.value.id}"
      },
      {
        Sid    = "FullAccessOwnBucket"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetObjectVersion",
          "s3:DeleteObjectVersion",
        ]
        Resource = "arn:aws:s3:::${each.value.id}/*"
      }
    ]
  })
}