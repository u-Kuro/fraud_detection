import numpy as np
import pytest
from unittest.mock import MagicMock

from services.train_model.src.modules.schemas.mlflow import MLFlowRegisteredModelInfo


def test_save_and_register_model_returns_registered_model_info(mocker):
    mock_module = mocker.patch(
        "services.train_model.src.repositories.mlflow.registered_model.mlflow_module"
    )
    mock_info = MagicMock()
    mock_info.run_id = "run-abc"
    mock_info.model_id = "model-123"
    mock_info.registered_model_version = 5
    mock_module.sklearn.log_model.return_value = mock_info
    mocker.patch(
        "services.train_model.src.repositories.mlflow.registered_model.infer_signature",
        return_value=MagicMock(),
    )

    from services.train_model.src.repositories.mlflow.registered_model import save_and_register_model
    rng = np.random.default_rng(0)
    mock_model = MagicMock()
    mock_model.predict.return_value = rng.random(4)
    result = save_and_register_model(model=mock_model, X_test_samples=rng.random((4, 3)))
    assert isinstance(result, MLFlowRegisteredModelInfo)


def test_save_and_register_model_raises_on_non_int_version(mocker):
    mock_module = mocker.patch(
        "services.train_model.src.repositories.mlflow.registered_model.mlflow_module"
    )
    mock_info = MagicMock()
    mock_info.run_id = "run-abc"
    mock_info.model_id = "model-123"
    mock_info.registered_model_version = "not_an_int"
    mock_module.sklearn.log_model.return_value = mock_info
    mocker.patch(
        "services.train_model.src.repositories.mlflow.registered_model.infer_signature",
        return_value=MagicMock(),
    )

    from services.train_model.src.repositories.mlflow.registered_model import save_and_register_model
    rng = np.random.default_rng(0)
    mock_model = MagicMock()
    mock_model.predict.return_value = rng.random(4)
    with pytest.raises(RuntimeError):
        save_and_register_model(model=mock_model, X_test_samples=rng.random((4, 3)))


def test_save_and_register_model_returns_correct_version(mocker):
    mock_module = mocker.patch(
        "services.train_model.src.repositories.mlflow.registered_model.mlflow_module"
    )
    mock_info = MagicMock()
    mock_info.run_id = "run-abc"
    mock_info.model_id = "model-123"
    mock_info.registered_model_version = 3
    mock_module.sklearn.log_model.return_value = mock_info
    mocker.patch(
        "services.train_model.src.repositories.mlflow.registered_model.infer_signature",
        return_value=MagicMock(),
    )

    from services.train_model.src.repositories.mlflow.registered_model import save_and_register_model
    rng = np.random.default_rng(0)
    mock_model = MagicMock()
    mock_model.predict.return_value = rng.random(4)
    result = save_and_register_model(model=mock_model, X_test_samples=rng.random((4, 3)))
    assert result.model_version == 3
