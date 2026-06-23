from typing import Literal, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field

class PipelineStateRow(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    state:             Literal["drift_pending", "train_pending", "promoting"]
    training_approved: bool            = False
    promote_approved:  bool            = False
    run_id:            Optional[str]   = None
    model_version:     Optional[int]   = None
    dataset_min_date:  Optional[datetime] = None
    dataset_max_date:  Optional[datetime] = None
    drift_slack_ts:    Optional[str]   = None
    promote_slack_ts:  Optional[str]   = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DeployedModelRow(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    model_id:         int
    model_name:       str
    model_version:    int
    dataset_min_date: Optional[datetime]
    dataset_max_date: datetime
    status:           Literal["promoting", "active"]
    promoted_at:      datetime