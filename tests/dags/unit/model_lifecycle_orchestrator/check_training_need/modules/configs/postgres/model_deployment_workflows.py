from dags.model_lifecycle_orchestrator.check_training_need.modules.configs.postgres.model_deployment_workflows import ModelDeploymentWorkflowsConfig, ReservedModelDeploymentWorkflowLabels, ExpiredModelDeploymentWorkflowsLabels

def test_config_challenger_model_expiration_days():
    assert ModelDeploymentWorkflowsConfig.challenger_model_expiration_days == 7

def test_reserved_labels_is_str_enum():
    from enum import StrEnum
    assert issubclass(ReservedModelDeploymentWorkflowLabels, StrEnum)

def test_expired_labels_is_str_enum():
    from enum import StrEnum
    assert issubclass(ExpiredModelDeploymentWorkflowsLabels, StrEnum)

def test_reserved_labels_has_registered_model_name():
    assert "registered_model_name" in ReservedModelDeploymentWorkflowLabels.registered_model_name

def test_expired_labels_has_id():
    assert "id" in ExpiredModelDeploymentWorkflowsLabels.id

def test_expired_labels_has_mlflow_run_id():
    assert "mlflow_run_id" in ExpiredModelDeploymentWorkflowsLabels.mlflow_run_id
