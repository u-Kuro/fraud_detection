from pydantic import BaseModel, ConfigDict

from shared.modules.schemas import FraudClassifierFeatures, FraudClassifierLabel, FraudClassificationPrediction, FraudClassificationProbability

class FraudClassifierConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    FRAUD_CLASSIFIER_FEATURES: list[str] = list(
        FraudClassifierFeatures.model_fields.keys()
    )
    FRAUD_CLASSIFIER_LABEL: str = next(
        iter(FraudClassifierLabel.model_fields.keys())
    )
    FRAUD_CLASSIFIER_PREDICTION_LABEL: str = next(
        iter(FraudClassificationPrediction.model_fields.keys())
    )
    FRAUD_CLASSIFIER_PROBABILITY_LABEL: str = next(
        iter(FraudClassificationProbability.model_fields.keys())
    )

fraud_classifier_config = FraudClassifierConfig()