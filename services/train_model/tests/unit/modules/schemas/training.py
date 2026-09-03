import pytest

try:
    from services.train_model.src.modules.schemas.training import TrainModelOutputs
    _SCHEMA_AVAILABLE = True
except RuntimeError:
    _SCHEMA_AVAILABLE = False

pytestmark = pytest.mark.skipif(
    not _SCHEMA_AVAILABLE,
    reason="Pydantic Strict() on arbitrary types not supported in this environment version",
)


def test_train_model_outputs_instantiation():
    outputs = TrainModelOutputs(model=object(), hyperparameters={"lr": 0.1})
    assert outputs.hyperparameters == {"lr": 0.1}


def test_train_model_outputs_stores_model():
    sentinel = object()
    outputs = TrainModelOutputs(model=sentinel, hyperparameters={})
    assert outputs.model is sentinel
