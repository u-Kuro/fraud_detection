from datetime import datetime

from pydantic import BaseModel, ConfigDict

class ModelDeployment(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    model_id:         int
    model_name:       str
    model_version:    int
    dataset_min_date: datetime | None
    dataset_max_date: datetime
    status:           bool
    promoted_at:      datetime