
# ─────────────────────────────────────────────────────────────────────────────
# OIDC Provider — registered once for the EKS cluster.
# Tells IAM to trust tokens issued by the cluster's built-in OIDC endpoint.
# ─────────────────────────────────────────────────────────────────────────────
data "tls_certificate" "eks" {
  url = var.eks_oidc_issuer_url
}

resource "aws_iam_openid_connect_provider" "eks" {
  url             = var.eks_oidc_issuer_url
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks.certificates[0].sha1_fingerprint]
}

locals {
  oidc_provider_id = replace(aws_iam_openid_connect_provider.eks.url, "https://", "")
}

# ─────────────────────────────────────────────────────────────────────────────
# Per-team IAM Role (IRSA).
# A pod annotates its ServiceAccount with this role ARN; the EKS Pod Identity
# Webhook injects a projected token so it can call sts:AssumeRoleWithWebIdentity.
# The condition pins the trust to exactly one service account per team namespace,
# preventing cross-team role assumption.
# ─────────────────────────────────────────────────────────────────────────────
data "aws_iam_policy_document" "team_assume_role" {
  for_each = var.teams

  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.eks.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider_id}:sub"
      values   = ["system:serviceaccount:${each.value.namespace}:${each.key}-sa"]
    }
    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider_id}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "team" {
  for_each           = var.teams
  name               = "${each.key}-irsa-role"
  assume_role_policy = data.aws_iam_policy_document.team_assume_role[each.key].json
}

# ─────────────────────────────────────────────────────────────────────────────
# ECR — push/replace own images only.
# The resource ARN uses the team-prefix convention (<team>/<repo>), so a team
# physically cannot write to another team's repository.
# GetAuthorizationToken is registry-wide (AWS does not support per-repo scoping).
# ─────────────────────────────────────────────────────────────────────────────
data "aws_iam_policy_document" "team_ecr" {
  for_each = { for k, v in var.teams : k => v if length(v.ecr_repos) > 0 }

  statement {
    sid       = "ECRAuthToken"
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }
  statement {
    sid    = "ECRPushOwnRepos"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:PutImage",
    ]
    resources = [
      for repo in each.value.ecr_repos :
      "arn:aws:ecr:${var.aws_region}:${var.aws_account_id}:repository/${each.key}/${repo}"
    ]
  }
  statement {
    sid    = "ECRPullOwnRepos"
    effect = "Allow"
    actions = [
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]
    resources = [
      for repo in each.value.ecr_repos :
      "arn:aws:ecr:${var.aws_region}:${var.aws_account_id}:repository/${each.key}/${repo}"
    ]
  }
}

resource "aws_iam_policy" "team_ecr" {
  for_each    = data.aws_iam_policy_document.team_ecr
  name        = "${each.key}-ecr-policy"
  description = "ECR push/pull for ${each.key} team repositories only"
  policy      = each.value.json
}

resource "aws_iam_role_policy_attachment" "team_ecr" {
  for_each   = aws_iam_policy.team_ecr
  role       = aws_iam_role.team[each.key].name
  policy_arn = each.value.arn
}

# ─────────────────────────────────────────────────────────────────────────────
# S3 — team-owned bucket + shared bucket with scoped paths only.
# The ListBucket condition (s3:prefix) limits what keys are visible in the
# shared bucket, preventing a team from enumerating another team's paths.
# ─────────────────────────────────────────────────────────────────────────────
data "aws_iam_policy_document" "team_s3" {
  for_each = var.teams

  dynamic "statement" {
    for_each = each.value.s3_team_bucket != null ? [1] : []
    content {
      sid       = "S3TeamBucketObjects"
      effect    = "Allow"
      actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
      resources = ["arn:aws:s3:::${each.value.s3_team_bucket}/*"]
    }
  }
  dynamic "statement" {
    for_each = each.value.s3_team_bucket != null ? [1] : []
    content {
      sid       = "S3TeamBucketList"
      effect    = "Allow"
      actions   = ["s3:ListBucket"]
      resources = ["arn:aws:s3:::${each.value.s3_team_bucket}"]
    }
  }

  dynamic "statement" {
    for_each = length(each.value.shared_s3_paths) > 0 ? [1] : []
    content {
      sid    = "S3SharedBucketScopedObjects"
      effect = "Allow"
      actions = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
      resources = [
        for path in each.value.shared_s3_paths :
        "arn:aws:s3:::${var.shared_s3_bucket}/${path}/*"
      ]
    }
  }
  dynamic "statement" {
    for_each = length(each.value.shared_s3_paths) > 0 ? [1] : []
    content {
      sid       = "S3SharedBucketScopedList"
      effect    = "Allow"
      actions   = ["s3:ListBucket"]
      resources = ["arn:aws:s3:::${var.shared_s3_bucket}"]
      condition {
        test     = "StringLike"
        variable = "s3:prefix"
        values   = [for p in each.value.shared_s3_paths : "${p}/*"]
      }
    }
  }
}

resource "aws_iam_policy" "team_s3" {
  for_each    = data.aws_iam_policy_document.team_s3
  name        = "${each.key}-s3-policy"
  description = "S3 access for ${each.key} team"
  policy      = each.value.json
}

resource "aws_iam_role_policy_attachment" "team_s3" {
  for_each   = aws_iam_policy.team_s3
  role       = aws_iam_role.team[each.key].name
  policy_arn = each.value.arn
}

# ─────────────────────────────────────────────────────────────────────────────
# MWAA — web-login token + get-environment for teams with MWAA access.
# The Airflow RBAC role (scoping DAG visibility to the team's prefix) is
# configured separately inside the MWAA module via airflow_configuration_options.
# ─────────────────────────────────────────────────────────────────────────────
data "aws_iam_policy_document" "team_mwaa" {
  for_each = { for k, v in var.teams : k => v if v.has_mwaa_access }

  statement {
    sid    = "MWAALogin"
    effect = "Allow"
    actions = [
      "airflow:CreateWebLoginToken",
      "airflow:GetEnvironment",
    ]
    resources = [
      "arn:aws:airflow:${var.aws_region}:${var.aws_account_id}:environment/${var.mwaa_environment_name}"
    ]
  }
}

resource "aws_iam_policy" "team_mwaa" {
  for_each    = data.aws_iam_policy_document.team_mwaa
  name        = "${each.key}-mwaa-policy"
  description = "MWAA access for ${each.key} team"
  policy      = each.value.json
}

resource "aws_iam_role_policy_attachment" "team_mwaa" {
  for_each   = aws_iam_policy.team_mwaa
  role       = aws_iam_role.team[each.key].name
  policy_arn = each.value.arn
}