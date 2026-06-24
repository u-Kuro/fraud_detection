# from pydantic import BaseModel
#
# from shared.schemas import FraudClassifierFeatures, FraudClassifierLabel
#
# class FraudClassifierConfig(BaseModel):
#     FRAUD_CLASSIFIER_FEATURES: list[str] = FraudClassifierFeatures.model_fields.keys()
#     FRAUD_CLASSIFIER_LABEL: list[str] = FraudClassifierLabel.model_fields.keys()[0]
#
# fraud_classifier_config = FraudClassifierConfig()