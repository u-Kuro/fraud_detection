resource "aws_s3_bucket" "dags" {
  bucket        = var.dags_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket" "mlflow" {
  bucket        = var.mlflow_bucket_name
  force_destroy = true
}
