from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator, Field, StrictFloat, StrictBool

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel

class FraudClassificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transaction_id: UUID

    transaction_timestamp: datetime

    @field_validator("transaction_timestamp")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        return v.astimezone(timezone.utc)

    amount: StrictFloat
    v1: StrictFloat
    v2: StrictFloat
    v3: StrictFloat
    v4: StrictFloat
    v5: StrictFloat
    v6: StrictFloat
    v7: StrictFloat
    v8: StrictFloat
    v9: StrictFloat
    v10: StrictFloat
    v11: StrictFloat
    v12: StrictFloat
    v13: StrictFloat
    v14: StrictFloat
    v15: StrictFloat
    v16: StrictFloat
    v17: StrictFloat
    v18: StrictFloat
    v19: StrictFloat
    v20: StrictFloat
    v21: StrictFloat
    v22: StrictFloat
    v23: StrictFloat
    v24: StrictFloat
    v25: StrictFloat
    v26: StrictFloat
    v27: StrictFloat
    v28: StrictFloat

class FraudClassificationResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    is_fraud_prediction: StrictBool
    is_fraud_probability: StrictFloat = Field(..., ge=0.0, le=1.0)

class FraudClassificationOutput(DeployedModel, FraudClassificationRequest, FraudClassificationResponse):
    model_config = ConfigDict(strict=True, extra="forbid")

    is_fraud: StrictBool | None = None