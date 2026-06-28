from pydantic import ConfigDict, Field, UUID4

from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel
from shared.modules.schemas import FraudClassifierFeatures, FraudClassifierLabel, FraudClassificationResponse

class FraudClassificationRequest(FraudClassifierFeatures):
    model_config = ConfigDict(strict=True, extra="forbid")
    transaction_id: UUID4 = Field(..., strict=False)

class FraudClassificationOutput(DeployedModel, FraudClassificationRequest, FraudClassificationResponse, FraudClassifierLabel):
    model_config = ConfigDict(strict=True, extra="forbid")