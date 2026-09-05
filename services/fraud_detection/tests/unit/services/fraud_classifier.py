from datetime import datetime, timezone
from uuid import uuid4, UUID

import pytest
from pytest_mock import MockerFixture

from services.fraud_detection.src.modules.configs.fraud_classifier import FraudClassifierConfig
from services.fraud_detection.src.modules.schemas.inferences.fraud_classification import FraudClassificationRequest
from services.fraud_detection.src.repositories.mlflow.models import MlflowModel
from services.fraud_detection.src.services.fraud_classifier import FraudClassifier
from services.shared.src.modules.schemas.models_dataset.fraud_classification import FraudClassificationFeaturesKeys
from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

class TestFraudClassifier:
    @staticmethod
    def make_model(**overrides) -> dict:
        data = {
            "model_name": "value",
            "model_version": 1
        }
        data.update(overrides)
        return data

    @staticmethod
    def make_request(**overrides) -> dict:
        data = {
            TransactionInferences.transaction_id.key: str(uuid4()),
            FraudClassificationFeaturesKeys.transaction_timestamp: datetime.now().isoformat(),
            FraudClassificationFeaturesKeys.amount: "1.0",
            **{
                key: "1.0" for key in FraudClassificationFeaturesKeys
                if key.startswith("v") and key[1:].isdigit()
            },
        }
        data.update(overrides)
        return data

    def test_identity(self):
        assert issubclass(FraudClassifier, MlflowModel)

    def test_classify(self, mocker: MockerFixture):
        model_data = self.make_model()
        request_data = self.make_request()
        fraud_probability = 1.0

        fraud_classifier = FraudClassifier(**model_data)
        mocker.patch.object(
            target=fraud_classifier.model,
            attribute="predict_proba",
            return_value=[[1.0 - fraud_probability, fraud_probability]]
        )
        output = fraud_classifier.classify(
            FraudClassificationRequest(**request_data)
        )

        for key, expected in model_data.items():
            actual = getattr(output, key)

            assert expected == actual

        for key, expected in request_data.items():
            actual = getattr(output, key)

            match key:
                case TransactionInferences.transaction_id.key:
                    assert actual == UUID(expected)
                case FraudClassificationFeaturesKeys.transaction_timestamp:
                    assert actual == datetime.fromisoformat(expected).astimezone(timezone.utc)
                case FraudClassificationFeaturesKeys.amount:
                    assert actual == pytest.approx(float(expected))
                case _ if key.startswith("v") and key[1:].isdigit():
                    assert actual == pytest.approx(float(expected))
                case _:
                    raise ValueError(f"Unexpected key: {key}")

        assert output.is_fraud is None
        assert output.is_fraud_probability == pytest.approx(fraud_probability)
        assert output.is_fraud_probability > FraudClassifierConfig.classification_threshold
