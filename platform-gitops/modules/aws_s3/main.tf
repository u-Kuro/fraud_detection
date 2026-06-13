resource "aws_s3_bucket" "mlflow" {
  bucket        = var.mlflow_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket" "mle" {
  bucket        = var.mle_bucket_name
  force_destroy = true
}