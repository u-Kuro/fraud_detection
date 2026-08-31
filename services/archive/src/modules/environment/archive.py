from datetime import datetime

from pydantic_settings import BaseSettings, SettingsConfigDict

class ArchiveEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    TRANSACTION_INFERENCES_ISO_DATETIME_CUTOFF: datetime

archive_environment = ArchiveEnvironment()