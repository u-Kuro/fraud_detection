from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.airflow.xcom import DriftCheckResult

def test_drift_check_result_is_pydantic_model():
    from pydantic import BaseModel
    assert issubclass(DriftCheckResult, BaseModel)

def test_drift_check_result_has_drift_detected_field():
    assert "drift_detected" in DriftCheckResult.model_fields

def test_drift_check_result_has_drift_summary_field():
    assert "drift_summary" in DriftCheckResult.model_fields
