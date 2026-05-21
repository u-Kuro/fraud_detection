from pydantic import BaseModel, ConfigDict, Field

class DriftReportArguments(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    days: int = Field(7, description="Days of recent inference logs to use as the current window")
    minimum_rows: int = Field(30, description="Minimum rows needed to run a report")
    drift_threshold: float = Field(0.30, description="Share-drifted threshold that triggers retraining")