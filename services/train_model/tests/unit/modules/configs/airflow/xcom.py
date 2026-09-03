from enum import StrEnum

from services.train_model.src.modules.configs.airflow.xcom import TrainModelXComKeys


def test_train_model_xcom_keys_is_str_enum():
    assert issubclass(TrainModelXComKeys, StrEnum)


def test_model_trained_at_datetime_key():
    assert TrainModelXComKeys.model_trained_at_datetime == "model_trained_at_datetime"


def test_model_mlflow_run_id_key():
    assert TrainModelXComKeys.model_mlflow_run_id == "model_mlflow_run_id"


def test_model_name_key():
    assert TrainModelXComKeys.model_name == "model_name"


def test_model_version_key():
    assert TrainModelXComKeys.model_version == "model_version"


def test_model_f1_score_key():
    assert TrainModelXComKeys.model_f1_score == "model_f1_score"


def test_all_keys_are_strings():
    for key in TrainModelXComKeys:
        assert isinstance(key.value, str)
