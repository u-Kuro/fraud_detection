# ADMIN
data "aws_caller_identity" "admin" {}
resource "aws_iam_role" "admin" {
  name = "admin_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = {
        AWS = "arn:aws:iam::${data.aws_caller_identity.admin.account_id}:root"
      }
      Action = "sts:AssumeRole"
    }]
  })
}
resource "aws_iam_role_policy_attachment" "owner_admin" {
  role       = aws_iam_role.admin.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
# TEAMS
resource "aws_iam_user" "teams" {
  for_each = var.team_names
  name = each.value
}
resource "aws_iam_access_key" "teams" {
  for_each = aws_iam_user.teams
  user     = each.value.name
}
#
# # =========================================================================
# # 1. THE PERMISSIONS POLICY (What actions are allowed)
# # =========================================================================
# resource "aws_iam_policy" "teams" {
#   name        = "S3ReadOnlyPolicy"
#   description = "Allows reading files from S3"
#
#   # This is the Policy Document (JSON text)
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Effect   = "Allow"
#         Action   = ["s3:GetObject", "s3:ListBucket"]
#         Resource = "*"
#       }
#     ]
#   })
# }
# # =========================================================================
# # 4. THE POLICY ATTACHMENT (Giving the hat its powers)
# # =========================================================================
# # This block connects the permissions (Step 1) directly to the Role (Step 3).
# resource "aws_iam_role_policy_attachment" "role_attach" {
#   role       = aws_iam_role.my_role.name         # The Role (Hat)
#   policy_arn = aws_iam_policy.s3_read_only.arn   # The Policy (Power)
# }
