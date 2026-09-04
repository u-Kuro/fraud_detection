from pydantic import StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class ECREnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    DRIFT_CHECK_IMAGE: StrictStr
    TRAIN_MODEL_IMAGE: StrictStr
    ARCHIVE_IMAGE: StrictStr

ecr_environment = ECREnvironment()