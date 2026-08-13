# TEAMS' SSM PARAMETER STORE PERMISSIONS
resource "aws_iam_role_policy" "teams_ssm_parameter" {
  for_each = local.ssm_parameter.users.teams
  role     = local.iam.users.teams[each.key].role.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "ssm:*"
        Resource = [
          "${local.ssm_parameter_arn}/${local.ssm_parameter_users.teams[each.key].path}",
          "${local.ssm_parameter_arn}/${local.ssm_parameter_users.teams[each.key].path}/*",
        ]
      }
    ]
  })
}
