from datetime import datetime, timezone, timedelta
from uuid import uuid4

import pytest
from pydantic import ValidationError

from services.fraud_detection.src.modules.schemas.inferences.fraud_classification import FraudClassificationOutput, FraudClassificationRequest, FraudClassificationResponse

def valid_request_data() -> dict:
    return {
        "transaction_id": uuid4(),
        "transaction_timestamp": datetime.now(timezone.utc),
        "amount": 100.0,
        **{f"v{i}": float(i) for i in range(1, 29)},
    }

def test_request_instantiation():
    data = valid_request_data()
    req = FraudClassificationRequest(**data)
    assert req.amount == 100.0

def test_request_converts_timestamp_to_utc():
    data = valid_request_data()
    # Provide a non-UTC timezone
    data["transaction_timestamp"] = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone(timedelta(hours=5)))
    req = FraudClassificationRequest(**data)
    assert req.transaction_timestamp.tzinfo == timezone.utc

def test_request_forbids_extra_fields():
    data = valid_request_data()
    data["extra"] = "boom"
    with pytest.raises(ValidationError):
        FraudClassificationRequest(**data)

def test_request_amount_must_be_numeric():
    # Pydantic 2.x StrictFloat accepts Python int in Python-mode construction;
    # it rejects non-numeric types regardless
    data = valid_request_data()
    data["amount"] = "not_a_number"
    with pytest.raises(ValidationError):
        FraudClassificationRequest(**data)

def test_request_v_fields_must_be_numeric():
    data = valid_request_data()
    data["v1"] = "invalid"
    with pytest.raises(ValidationError):
        FraudClassificationRequest(**data)

def test_request_missing_v_field_raises():
    data = valid_request_data()
    del data["v28"]
    with pytest.raises(ValidationError):
        FraudClassificationRequest(**data)

def test_request_has_all_28_v_fields():
    data = valid_request_data()
    req = FraudClassificationRequest(**data)
    for i in range(1, 29):
        assert hasattr(req, f"v{i}")

def test_response_instantiation():
    resp = FraudClassificationResponse(is_fraud_prediction=True, is_fraud_probability=0.9)
    assert resp.is_fraud_prediction is True
    assert resp.is_fraud_probability == 0.9

def test_response_probability_ge_zero():
    with pytest.raises(ValidationError):
        FraudClassificationResponse(is_fraud_prediction=False, is_fraud_probability=-0.1)

def test_response_probability_le_one():
    with pytest.raises(ValidationError):
        FraudClassificationResponse(is_fraud_prediction=False, is_fraud_probability=1.1)

def test_response_is_fraud_prediction_must_be_strict_bool():
    with pytest.raises(ValidationError):
        FraudClassificationResponse(is_fraud_prediction=1, is_fraud_probability=0.5)

def test_output_instantiation():
    data = valid_request_data()
    output = FraudClassificationOutput(
        **data,
        is_fraud=None,
        is_fraud_prediction=True,
        is_fraud_probability=0.8,
        model_name="xgboost",
        model_version=1,
    )
    assert output.is_fraud is None
    assert output.is_fraud_prediction is True

def test_output_is_fraud_defaults_to_none():
    data = valid_request_data()
    output = FraudClassificationOutput(
        **data,
        is_fraud_prediction=False,
        is_fraud_probability=0.1,
        model_name="xgboost",
        model_version=1,
    )
    assert output.is_fraud is None

def test_output_is_fraud_accepts_bool():
    data = valid_request_data()
    output = FraudClassificationOutput(
        **data,
        is_fraud=True,
        is_fraud_prediction=True,
        is_fraud_probability=0.9,
        model_name="xgboost",
        model_version=1,
    )
    assert output.is_fraud is True