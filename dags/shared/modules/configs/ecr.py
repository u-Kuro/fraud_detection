@dataclass(frozen=True)
class ECRConfig:
    ECR_URL: str = "ministack:5000"