from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from services.fraud_detection.src.modules.schemas.inferences.fraud_classification import FraudClassificationOutput
from services.fraud_detection.src.repositories.postgres.transaction_inferences import insert_transaction_inference

def make_output() -> FraudClassificationOutput:
    return FraudClassificationOutput(
        transaction_id=uuid4(),
        transaction_timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        amount=50.0,
        **{f"v{i}": float(i) for i in range(1, 29)},
        is_fraud=None,
        is_fraud_prediction=True,
        is_fraud_probability=0.9,
        model_name="xgboost",
        model_version=1,
    )

def make_session_mock():
    mock_inner = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.__enter__ = MagicMock(return_value=mock_inner)
    mock_ctx.__exit__ = MagicMock(return_value=False)
    mock_sm = MagicMock()
    mock_sm.begin.return_value = mock_ctx
    return mock_sm

def test_insert_transaction_inference_executes_insert(mocker):
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.transaction_inferences.sql_session",
        make_session_mock(),
    )
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.transaction_inferences.PostgresConfig"
    ).project_id.return_value = uuid4()

    insert_transaction_inference(make_output())

def test_insert_transaction_inference_with_is_fraud_true(mocker):
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.transaction_inferences.sql_session",
        make_session_mock(),
    )
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.transaction_inferences.PostgresConfig"
    ).project_id.return_value = uuid4()

    insert_transaction_inference(make_output(), is_fraud=True)

def test_insert_transaction_inference_with_is_fraud_false(mocker):
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.transaction_inferences.sql_session",
        make_session_mock(),
    )
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.transaction_inferences.PostgresConfig"
    ).project_id.return_value = uuid4()

    insert_transaction_inference(make_output(), is_fraud=False)

def test_insert_transaction_inference_default_is_fraud_none(mocker):
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.transaction_inferences.sql_session",
        make_session_mock(),
    )
    mocker.patch(
        "services.fraud_detection.src.repositories.postgres.transaction_inferences.PostgresConfig"
    ).project_id.return_value = uuid4()

    insert_transaction_inference(make_output())