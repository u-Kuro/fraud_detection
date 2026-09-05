from datetime import datetime, timezone
from uuid import uuid4, UUID

import pytest
from pydantic import ValidationError

from services.fraud_detection.src.modules.schemas.inferences.fraud_classification import FraudClassificationRequest, FraudClassificationResponse, FraudClassificationOutput
from services.shared.src.modules.schemas.models_dataset.fraud_classification import FraudClassificationFeaturesKeys
from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

class TestFraudClassificationRequest:
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

    def test_values(self):
        data = self.make_request()
        values = FraudClassificationRequest(**data)

        for key, expected in data.items():
            actual = getattr(values, key)

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

    def test_failure_for_extra_field(self):
        data = self.make_request(extra=0)
        with pytest.raises(ValidationError):
            FraudClassificationRequest(**data)

class TestFraudClassificationResponse:
    @staticmethod
    def make_response(**overrides) -> dict:
        data = {
            TransactionInferences.is_fraud_prediction.key: True,
            TransactionInferences.is_fraud_probability.key: 1.0
        }
        data.update(overrides)
        return data

    def test_values(self):
        data = self.make_response()
        values = FraudClassificationResponse(**data)

        for key, expected in data.items():
            actual = getattr(values, key)

            if isinstance(expected, float):
                assert actual == pytest.approx(expected)
            else:
                assert expected == actual

        assert 1.0 >= getattr(values, TransactionInferences.is_fraud_probability.key) >= 0.0

    def test_failure_for_extra_field(self):
        data = self.make_response(extra=0)
        with pytest.raises(ValidationError):
            FraudClassificationResponse(**data)

class TestFraudClassificationOutput:
    @staticmethod
    def make_output(**overrides) -> dict:
        data = {
            **TestFraudClassificationRequest.make_request(),
            **TestFraudClassificationResponse.make_response()
        }
        data.update(overrides)
        return data

    def test_values(self):
        data = self.make_output()
        values = FraudClassificationOutput(**data)

        for key, expected in data.items():
            actual = getattr(values, key)

            if isinstance(expected, float):
                assert actual == pytest.approx(expected)
            else:
                assert expected == actual

    def test_failure_for_extra_field(self):
        data = self.make_output(extra=0)
        with pytest.raises(ValidationError):
            FraudClassificationOutput(**data)