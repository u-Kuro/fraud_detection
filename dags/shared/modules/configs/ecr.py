from dataclasses import dataclass

@dataclass(frozen=True)
class ECRConfig:
    ECR_URL: str = "ministack:5000"

@dataclass(frozen=True)
class ECRImageKeys:
    # TODO - check image names in terraform
    drift_check: str = "drift_check"
    train_model: str = "train_model"

@dataclass(frozen=True)
class ECRSecretKeys:
    # TODO - check secrets keys in terraform
    ecr_secret: str = "ecr_secret"