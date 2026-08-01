resource "aws_s3_bucket" "mlflow" {
  bucket        = "mlflow"
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "mlflow_bucket_versioning" {   # renamed
  bucket = aws_s3_bucket.mlflow.id
  versioning_configuration { status = "Enabled" }
  depends_on = [aws_s3_bucket.mlflow]
}

resource "aws_s3_bucket" "mwaa" {
  bucket        = "mwaa"
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "mwaa_bucket_versioning" {      # was "mwaa_bucket_versioning" (duplicate name — fixed)
  bucket = aws_s3_bucket.mwaa.id
  versioning_configuration { status = "Enabled" }
  depends_on = [aws_s3_bucket.mwaa]
}

# ── Per-team dedicated buckets (for teams with s3_team_bucket set) ──────────
resource "aws_s3_bucket" "team" {
  for_each      = { for k, v in var.teams : k => v if v.s3_team_bucket != null }
  bucket        = each.value.s3_team_bucket
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "team_bucket_versioning" {
  for_each = aws_s3_bucket.team
  bucket   = each.value.id
  versioning_configuration { status = "Enabled" }
  depends_on = [aws_s3_bucket.team]
}