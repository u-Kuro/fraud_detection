from datetime import datetime, timezone
from unittest.mock import MagicMock
from uuid import uuid4

from services.fraud_detection.src.modules.schemas.inferences.fraud_classification import FraudClassificationOutput, FraudClassificationRequest
from services.fraud_detection.src.modules.schemas.mlflow import DeployedModel
from services.fraud_detection.src.services.fraud_classifier import FraudClassifier

def make_request() -> FraudClassificationRequest:
    return FraudClassificationRequest(
        transaction_id=uuid4(),
        transaction_timestamp=datetime(2025, 1, 1, tzinfo=timezone.utc),
        amount=100.0,
        **{f"v{i}": float(i) for i in range(1, 29)},
    )

def make_classifier(mocker) -> FraudClassifier:
    mock_mlflow = mocker.patch(
        "services.fraud_detection.src.repositories.mlflow.models.mlflow"
    )
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = [[0.1, 0.9]]
    mock_mlflow.sklearn.load_model.return_value = mock_model
    dm = DeployedModel(model_name="xgboost", model_version=1)
    return FraudClassifier(deployed_model=dm)

def test_fraud_classifier_classify_returns_output(mocker):
    clf = make_classifier(mocker)
    req = make_request()
    result = clf.classify(req)
    assert isinstance(result, FraudClassificationOutput)

def test_fraud_classifier_classify_uses_probability(mocker):
    clf = make_classifier(mocker)
    clf.model.predict_proba.return_value = [[0.1, 0.85]]
    req = make_request()
    result = clf.classify(req)
    assert abs(result.is_fraud_probability - 0.85) < 1e-9

def test_fraud_classifier_classify_prediction_above_threshold(mocker):
    clf = make_classifier(mocker)
    clf.model.predict_proba.return_value = [[0.1, 0.9]]
    req = make_request()
    result = clf.classify(req)
    assert result.is_fraud_prediction is True

def test_fraud_classifier_classify_prediction_below_threshold(mocker):
    clf = make_classifier(mocker)
    clf.model.predict_proba.return_value = [[0.8, 0.2]]
    req = make_request()
    result = clf.classify(req)
    assert result.is_fraud_prediction is False

def test_fraud_classifier_classify_sets_is_fraud_none(mocker):
    clf = make_classifier(mocker)
    req = make_request()
    result = clf.classify(req)
    assert result.is_fraud is None

def test_fraud_classifier_classify_converts_timestamp_to_int(mocker):
    clf = make_classifier(mocker)
    req = make_request()
    clf.classify(req)
    called_df = clf.model.predict_proba.call_args[0][0]
    assert called_df["transaction_timestamp"].dtype in ("int64", "int32")

def test_fraud_classifier_classify_includes_model_name_version(mocker):
    clf = make_classifier(mocker)
    req = make_request()
    result = clf.classify(req)
    assert result.model_name == "xgboost"
    assert result.model_version == 1
