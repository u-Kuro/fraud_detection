from pydantic import BaseModel, ConfigDict

class ArchivingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    BATCH_SIZE: int = 50_000

archiving_config = ArchivingConfig()