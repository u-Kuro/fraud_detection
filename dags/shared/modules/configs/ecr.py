from pydantic import BaseModel, ConfigDict

class ECRConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    ECR_URL: str = "ministack:5000"

ecr_config = ECRConfig()