from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.k8s.environments import DriftCheckEnvironmentKeys

def test_drift_check_env_keys_is_str_enum():
    from enum import StrEnum
    assert issubclass(DriftCheckEnvironmentKeys, StrEnum)

def test_active_model_deployment_mlflow_run_id():
    assert DriftCheckEnvironmentKeys.ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID == "ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID"
