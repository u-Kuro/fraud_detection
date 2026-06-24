from pydantic import BaseModel, ConfigDict, Field, UUID4

class FraudClassificationPrediction(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    is_fraud_prediction: bool

class FraudClassificationProbability(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    is_fraud_probability: float = Field(..., ge=0.0, le=1.0)

class FraudClassificationResponse(FraudClassificationPrediction, FraudClassificationProbability):
    model_config = ConfigDict(strict=True, extra="forbid")