from pydantic import BaseModel, ConfigDict

class FraudClassifierConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    CLASSIFICATION_THRESHOLD: float = 0.5

fraud_classifier_config = FraudClassifierConfig()