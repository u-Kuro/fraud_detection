from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ArchivingBatchResult(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    batch_number:     int   = Field(..., ge=1)
    rows_read:        int   = Field(..., ge=0)
    rows_deleted:     int   = Field(..., ge=0)
    parquet_key:      str
    cutoff_timestamp: datetime
    elapsed_ms:       float = Field(..., ge=0.0)