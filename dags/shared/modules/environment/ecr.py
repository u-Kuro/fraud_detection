from pydantic_settings import BaseSettings, SettingsConfigDict

class ECREnvironment(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True
    )

    DRIFT_CHECK_IMAGE: str
    TRAIN_MODEL_IMAGE: str
    ARCHIVE_IMAGE: str

ecr_environment = ECREnvironment()