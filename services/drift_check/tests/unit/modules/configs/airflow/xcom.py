from enum import StrEnum

from services.drift_check.src.modules.configs.airflow.xcom import DriftCheckXComKeys

def test_drift_check_xcom_keys_is_str_enum():
    assert issubclass(DriftCheckXComKeys, StrEnum)

def test_drift_detected_value():
    assert DriftCheckXComKeys.drift_detected == "drift_detected"

def test_drift_summary_value():
    assert DriftCheckXComKeys.drift_summary == "drift_summary"

def test_all_keys_are_strings():
    for key in DriftCheckXComKeys:
        assert isinstance(key.value, str)
