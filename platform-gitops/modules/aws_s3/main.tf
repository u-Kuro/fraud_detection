resource "aws_s3_bucket" "mlflow" {
  bucket        = "mlflow"
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "mwaa_bucket_versioning" {
  bucket = aws_s3_bucket.mlflow.id

  versioning_configuration {
    status = "Enabled"
  }

  depends_on = [aws_s3_bucket.mlflow]
}

resource "aws_s3_bucket" "mle" {
  bucket        = "mle"
  force_destroy = true
}
resource "aws_s3_bucket_versioning" "mwaa_bucket_versioning" {
  bucket = aws_s3_bucket.mle.id

  versioning_configuration {
    status = "Enabled"
  }

  depends_on = [aws_s3_bucket.mle]
}