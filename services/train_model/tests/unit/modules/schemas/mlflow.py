import pytest
from pydantic import ValidationError

from services.train_model.src.modules.schemas.mlflow import MLflowRegisteredModelInfo


def test_mlflow_registered_model_info_instantiation():
    info = MLflowRegisteredModelInfo(
        run_id="run-abc", model_id="model-123", model_name="xgboost", model_version=1
    )
    assert info.run_id == "run-abc"
    assert info.model_version == 1


def test_model_version_must_be_strict_int():
    with pytest.raises(ValidationError):
        MLflowRegisteredModelInfo(
            run_id="run-abc", model_id="m", model_name="x", model_version=1.0
        )


def test_run_id_must_be_strict_str():
    with pytest.raises(ValidationError):
        MLflowRegisteredModelInfo(
            run_id=123, model_id="m", model_name="x", model_version=1
        )
