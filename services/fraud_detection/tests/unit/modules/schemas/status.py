import pytest
from pydantic import ValidationError

from services.fraud_detection.src.modules.schemas.status import StatusResponse

class TestStatusResponse:
    @staticmethod
    def make_data(**overrides) -> dict:
        data = {
            "status": "value"
        }
        data.update(overrides)
        return data

    def test_values(self):
        data = self.make_data()
        values = StatusResponse(**data)

        for key, expected in data.items():
            actual = getattr(values, key)

            assert expected == actual

    def test_failure_for_extra_field(self):
        data = self.make_data(extra=0)
        with pytest.raises(ValidationError):
            StatusResponse(**data)