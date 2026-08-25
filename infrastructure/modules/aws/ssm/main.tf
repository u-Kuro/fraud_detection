# Allow teams to manage their own parameters
resource "aws_iam_user_policy" "teams_ssm_parameter" {
  for_each = var.ssm_teams
  user     = var.iam_teams_names[each.key]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "ssm:*"
        Resource = [
          local.ssm_teams_parameter_arns[each.key],
          "${local.ssm_teams_parameter_arns[each.key]}/*",
        ]
      }
    ]
  })
}
