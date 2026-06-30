from pydantic import ConfigDict, Field, UUID4

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel
from shared.modules.schemas import FraudClassificationFeatures, FraudClassificationLabel, FraudClassificationResponse

class FraudClassificationRequest(FraudClassificationFeatures):
    model_config = ConfigDict(strict=True, extra="forbid")
    transaction_id: UUID4 = Field(..., strict=False)

class FraudClassificationOutput(DeployedModel, FraudClassificationRequest, FraudClassificationResponse, FraudClassificationLabel):
    model_config = ConfigDict(strict=True, extra="forbid")