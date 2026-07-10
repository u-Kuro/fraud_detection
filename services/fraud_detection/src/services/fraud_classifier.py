import pandas as pd

from services.fraud_detection.src.modules.configs import fraud_classifier_config
from services.fraud_detection.src.modules.schemas import (
    FraudClassificationRequest,
    FraudClassificationOutput,
)
from services.fraud_detection.src.repositories.mlflow.models import MlflowModel
from services.shared.modules.schemas import FraudClassificationFeatures

class FraudClassifier(MlflowModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, class_name=self.__class__.__name__)

    def classify(
        self,
        transaction_details: FraudClassificationRequest
    ) -> FraudClassificationOutput:
        features = transaction_details.model_dump(
            include=FraudClassificationFeatures.model_fields.keys()
        )

        features_df = pd.DataFrame([features])
        features_df["transaction_timestamp"] = features_df[
            "transaction_timestamp"
        ].apply(lambda x: int(x.timestamp()))

        fraud_probability = float(self.model.predict_proba(features_df)[0][1])
        fraud_prediction = fraud_probability > fraud_classifier_config.CLASSIFICATION_THRESHOLD

        return FraudClassificationOutput(
            **transaction_details.model_dump(),
            is_fraud=None,
            is_fraud_probability=fraud_probability,
            is_fraud_prediction=fraud_prediction,
            model_name=self.deployed_model.model_name,
            model_version=self.deployed_model.model_version,
        )