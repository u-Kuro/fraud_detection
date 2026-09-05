import json
from uuid import uuid4, UUID

import pytest
from pydantic import ValidationError

from services.fraud_detection.src.modules.schemas.slack import TrainingValue, PromotionValue

class TestTrainingValue:
    @staticmethod
    def make_data(**overrides):
        data = {
            "workflow_id": str(uuid4()),
            "should_train_for_promotion": json.dumps(True)
        }
        data.update(overrides)
        return data

    def test_values(self):
        data = self.make_data()
        value = TrainingValue(**data)

        for key, expected in data.items():
            actual = getattr(value, key)

            match key:
                case "workflow_id":
                    assert actual == UUID(expected)
                case "should_train_for_promotion":
                    assert actual == json.loads(expected)
                case _:
                    raise ValueError(f"Unexpected key: {key}")

    def test_failure_for_extra_field(self):
        data = self.make_data(extra=0)
        with pytest.raises(ValidationError):
            TrainingValue(**data)

class TestPromotionValue:
    @staticmethod
    def make_data(**overrides):
        data = {
            "workflow_id": str(uuid4())
        }
        data.update(overrides)
        return data

    def test_values(self):
        data = self.make_data()
        value = PromotionValue(**data)

        for key, expected in data.items():
            actual = getattr(value, key)

            match key:
                case "workflow_id":
                    assert actual == UUID(expected)
                case _:
                    raise ValueError(f"Unexpected key: {key}")

    def test_failure_for_extra_field(self):
        data = self.make_data(extra=0)
        with pytest.raises(ValidationError):
            PromotionValue(**data)