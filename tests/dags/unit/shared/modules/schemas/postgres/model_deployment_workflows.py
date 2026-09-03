from dags.shared.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowState, ModelDeploymentWorkflows

def test_workflow_state_is_str_enum():
    from enum import StrEnum
    assert issubclass(ModelDeploymentWorkflowState, StrEnum)

def test_workflow_state_train_pending():
    assert ModelDeploymentWorkflowState.train_pending == "train_pending"

def test_workflow_state_promote_pending():
    assert ModelDeploymentWorkflowState.promote_pending == "promote_pending"

def test_workflow_state_reserved():
    assert ModelDeploymentWorkflowState.reserved == "reserved"

def test_workflow_tablename():
    assert ModelDeploymentWorkflows.__tablename__ == "model_deployment_workflows"

def test_workflow_has_state():
    assert hasattr(ModelDeploymentWorkflows, "state")

def test_workflow_has_mlflow_run_id():
    assert hasattr(ModelDeploymentWorkflows, "mlflow_run_id")

def test_workflow_has_registered_model_name():
    assert hasattr(ModelDeploymentWorkflows, "registered_model_name")

def test_workflow_has_registered_model_version():
    assert hasattr(ModelDeploymentWorkflows, "registered_model_version")

def test_workflow_has_slack_training_approval_message_ts():
    assert hasattr(ModelDeploymentWorkflows, "slack_training_approval_message_ts")

def test_workflow_has_slack_promotion_approval_message_ts():
    assert hasattr(ModelDeploymentWorkflows, "slack_promotion_approval_message_ts")
