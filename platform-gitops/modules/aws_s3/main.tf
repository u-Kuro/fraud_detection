resource "aws_s3_bucket" "dags" {
  bucket_name   = var.dags_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket" "mlflow" {
  bucket_name   = var.mlflow_bucket_name
  force_destroy = true
}
