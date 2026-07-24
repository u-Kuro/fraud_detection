from dataclasses import dataclass

@dataclass(frozen=True)
class K8sConfig:
    namespace: str = "default"

@dataclass(frozen=True)
class K8sConfigMapKeys:
    # TODO - check config map keys in terraform
    platform_infrastructure: str = "platform_infrastructure"

@dataclass(frozen=True)
class K8sSecretKeys:
    # TODO - check secret keys in terraform
    mle_pipeline_secret: str = "mle_pipeline_secret"