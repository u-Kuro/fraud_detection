from enum import Enum
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ModelDeploymentStatus(str, Enum):
    promoting = "promoting"
    active = "active"

class ModelDeployment(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    model_id:         int
    model_name:       str
    model_version:    int
    dataset_min_date: datetime | None
    dataset_max_date: datetime
    status:           ModelDeploymentStatus
    promoted_at:      datetime