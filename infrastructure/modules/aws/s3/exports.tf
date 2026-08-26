# Allow teams to see info of their S3 buckets
resource "aws_ssm_parameter" "teams_bucket_name" {
  for_each = aws_s3_bucket.teams
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/s3/bucket"
  type     = "String"
  value    = each.value.id

  depends_on = [
    # Waits until teams S3 resources are fully functional
    aws_s3_bucket.teams_mwaa
  ]
}
resource "aws_ssm_parameter" "teams_mwaa_bucket_name" {
  for_each = aws_s3_bucket.teams_mwaa
  name     = "/${var.ssm_teams_parameter_paths[each.key]}/s3/mwaa-bucket"
  type     = "String"
  value    = each.value.id

  depends_on = [
    # Waits until teams S3 resources are fully functional
    aws_s3_bucket.teams
  ]
}
