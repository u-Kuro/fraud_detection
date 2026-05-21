import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

@pytest.fixture
def sample_prediction_request():
    """Valid transaction payload matching your PredictionRequest schema."""
    return {
        "transaction_id": str(uuid.uuid4()),
        "transaction_timestamp": datetime.now(timezone.utc).isoformat(),
        "amount": 149.99,
        **{f"v{i}": 0.0 for i in range(1, 29)},  # 28 PCA features
    }

@pytest.fixture
def mock_mlflow_model_legitimate():
    """Fake model that returns fraud=0, prob=0.05."""
    model = MagicMock()
    model.predict.return_value = [0]
    model.predict_proba.return_value = [[0.95, 0.05]]
    return model

@pytest.fixture
def mock_mlflow_model_fraud():
    """Fake model that returns fraud=0, prob=0.05."""
    model = MagicMock()
    model.predict.return_value = [1]
    model.predict_proba.return_value = [[0.05, 0.95]]
    return model