from pydantic import BaseModel, ConfigDict

from shared.schemas import FraudClassifierFeatures, FraudClassifierLabel, FraudClassificationPrediction, FraudClassificationProbability

class FraudClassifierConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    FRAUD_CLASSIFIER_FEATURES: list[str] = FraudClassifierFeatures.model_fields.keys()
    FRAUD_CLASSIFIER_LABEL: str = FraudClassifierLabel.model_fields.keys()[0]
    FRAUD_CLASSIFIER_PREDICTION_LABEL: str = FraudClassificationPrediction.model_fields.keys()[0]
    FRAUD_CLASSIFIER_PROBABILITY_LABEL: str = FraudClassificationProbability.model_fields.keys()[0]

fraud_classifier_config = FraudClassifierConfig()