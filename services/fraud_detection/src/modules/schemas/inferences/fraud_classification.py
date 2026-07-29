from datetime import datetime, timezone

from pydantic import ConfigDict, Field, UUID4, BaseModel, field_validator

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel

class FraudClassificationRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")

    transaction_id: UUID4

    transaction_timestamp: datetime

    @field_validator("transaction_timestamp")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        return v.astimezone(timezone.utc)

    amount: float
    v1: float
    v2: float
    v3: float
    v4: float
    v5: float
    v6: float
    v7: float
    v8: float
    v9: float
    v10: float
    v11: float
    v12: float
    v13: float
    v14: float
    v15: float
    v16: float
    v17: float
    v18: float
    v19: float
    v20: float
    v21: float
    v22: float
    v23: float
    v24: float
    v25: float
    v26: float
    v27: float
    v28: float

class FraudClassificationResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    is_fraud_prediction: bool
    is_fraud_probability: float = Field(..., ge=0.0, le=1.0)

class FraudClassificationOutput(DeployedModel, FraudClassificationRequest, FraudClassificationResponse):
    model_config = ConfigDict(strict=True, extra="forbid")

    is_fraud: bool | None = None