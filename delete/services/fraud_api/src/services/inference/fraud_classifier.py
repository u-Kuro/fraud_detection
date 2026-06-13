import pandas as pd
from services.fraud_api.src.modules.schemas import (
    MlflowModelFeatures,
    TransactionDetails,
    TransactionClassification,
)
from services.fraud_api.src.repositories.mlflow.models import MlflowModel
from services.shared.observability import observe


class FraudClassifier(MlflowModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, class_name=self.__class__.__name__)

    @observe
    def classify(
        self, transaction_details: TransactionDetails
    ) -> TransactionClassification:
        features = transaction_details.model_dump(
            include=MlflowModelFeatures.model_fields.keys()
        )

        features_df = pd.DataFrame([features])
        features_df["transaction_timestamp"] = features_df[
            "transaction_timestamp"
        ].apply(lambda x: int(x.timestamp()))

        prediction = int(self.model.predict(data=features_df)[0])
        fraud_probability = self.model.predict_proba(features_df)[0][1]

        return TransactionClassification(
            **transaction_details.model_dump(),
            is_fraud=None,
            is_fraud_probability=float(fraud_probability),
            is_fraud_prediction=prediction == 1,
            model_name=self.deployed_model.model_name,
            model_version=self.deployed_model.model_version,
        )
