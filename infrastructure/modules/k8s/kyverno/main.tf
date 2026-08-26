# Create Kyverno release
resource "helm_release" "kyverno" {
  name             = "kyverno"
  repository       = "https://kyverno.github.io/kyverno"
  chart            = "kyverno"
  version          = "3.9.0" # v1.19.0 https://artifacthub.io/packages/helm/kyverno/kyverno/3.9.0
  namespace        = var.eks_kyverno_namespace
  create_namespace = true
  wait             = true
  wait_for_jobs    = true
}