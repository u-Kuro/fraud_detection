# TODO - 08/08/2026 - Continue here...
resource "kubernetes_config_map" "teams" {
  for_each = local.aws.users.teams

  metadata {
    name      = "base"
    namespace = each.value.kubernetes.namespace
  }

  data = {
    # INFRA URLS
  }
}

resource "kubernetes_secret" "teams" {
  for_each = local.aws.users.teams
  type     = "Opaque"

  metadata {
    name      = "base"
    namespace = each.value.kubernetes.namespace
  }

  data = {
    # SECRETS
  }
}

#name: CD
#
#on:
#  push:
#    branches: [main]
#
#env:
#  AWS_REGION: ap-southeast-1
#  ECR_REGISTRY: 123456789.dkr.ecr.ap-southeast-1.amazonaws.com
#  ECR_REPOSITORY: team-a-app
#  IMAGE_TAG: ${{ github.sha }}
#  DEPLOYMENT_NAME: team-a-app
#  NAMESPACE: team-a-namespace
#
#jobs:
#  deploy:
#    runs-on: ubuntu-latest
#
#    steps:
#      - name: Checkout
#        uses: actions/checkout@v4
#
#      - name: Configure AWS credentials
#        uses: aws-actions/configure-aws-credentials@v4
#        with:
#          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
#          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
#          aws-region: ${{ env.AWS_REGION }}
#
#      - name: Login to ECR
#        uses: aws-actions/amazon-ecr-login@v2
#
#      - name: Update kubeconfig
#        run: aws eks update-kubeconfig --name eks --region ${{ env.AWS_REGION }}
#
#      ...
#
#      - name: Wait for rollout
#        run: |
#          kubectl rollout status deployment/${{ env.DEPLOYMENT_NAME }} \
#            -n ${{ env.NAMESPACE }} \
#            --timeout=300s

resource "kubernetes_secret" "ecr_registry" {
  for_each = local.aws.users.teams
  type     = "kubernetes.io/dockerconfigjson"

  metadata {
    name      = "ecr-dockerconfigjson"
    namespace = each.value.kubernetes.namespace
  }

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        # Matches to original endpoint in EKS. In MiniStack's EKS (registries.yaml), it's set to redirect to MiniStack's ECR endpoint.
        (local.ecr.aws.endpoint) = {
          username = local.ecr.aws.token.username
          password = local.ecr.aws.token.password
          auth     = local.ecr.aws.token.authorization_token
        }
      }
    })
  }
}