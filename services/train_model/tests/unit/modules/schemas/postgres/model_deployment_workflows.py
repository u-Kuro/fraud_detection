import pytest
from pydantic import ValidationError

from services.train_model.src.modules.schemas.postgres.model_deployment_workflows import (
    ModelDeploymentWorkflowDatasetTimestamps,
)


def test_timestamps_instantiation():
    t = ModelDeploymentWorkflowDatasetTimestamps(
        model_dataset_min_iso_datetime="2025-01-01T00:00:00",
        model_dataset_max_iso_datetime="2025-06-01T00:00:00",
    )
    assert t.model_dataset_min_iso_datetime == "2025-01-01T00:00:00"


def test_timestamps_missing_field_raises():
    with pytest.raises(ValidationError):
        ModelDeploymentWorkflowDatasetTimestamps(
            model_dataset_min_iso_datetime="2025-01-01T00:00:00"
        )
