from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.airflow.xcom import DriftCheckXComKeys

def test_drift_check_xcom_keys_is_str_enum():
    from enum import StrEnum
    assert issubclass(DriftCheckXComKeys, StrEnum)

def test_drift_detected():
    assert DriftCheckXComKeys.drift_detected == "drift_detected"

def test_drift_summary():
    assert DriftCheckXComKeys.drift_summary == "drift_summary"
