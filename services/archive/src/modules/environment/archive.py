from datetime import datetime

from pydantic_settings import BaseSettings, SettingsConfigDict

class ArchiveEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    TRANSACTION_INFERENCES_ARCHIVE_CUTOFF_ISO_DATETIME: datetime

archive_environment = ArchiveEnvironment()