from services.shared.src.modules.schemas.postgres.model_deployment_workflows import ModelDeploymentWorkflowState, ModelDeploymentWorkflows

def test_model_deployment_workflow_state_train_pending():
    assert ModelDeploymentWorkflowState.train_pending == "train_pending"

def test_model_deployment_workflow_state_promote_pending():
    assert ModelDeploymentWorkflowState.promote_pending == "promote_pending"

def test_model_deployment_workflow_state_reserved():
    assert ModelDeploymentWorkflowState.reserved == "reserved"

def test_model_deployment_workflow_state_is_str_enum():
    from enum import StrEnum
    assert issubclass(ModelDeploymentWorkflowState, StrEnum)

def test_model_deployment_workflow_state_all_values():
    values = {s.value for s in ModelDeploymentWorkflowState}
    assert values == {"train_pending", "promote_pending", "reserved"}

def test_model_deployment_workflows_tablename():
    assert ModelDeploymentWorkflows.__tablename__ == "model_deployment_workflows"

def test_model_deployment_workflows_has_state():
    assert hasattr(ModelDeploymentWorkflows, "state")

def test_model_deployment_workflows_has_training_approved():
    assert hasattr(ModelDeploymentWorkflows, "training_approved")

def test_model_deployment_workflows_has_promotion_approved():
    assert hasattr(ModelDeploymentWorkflows, "promotion_approved")

def test_model_deployment_workflows_has_mlflow_run_id():
    assert hasattr(ModelDeploymentWorkflows, "mlflow_run_id")

def test_model_deployment_workflows_has_slack_training_approval_message_ts():
    assert hasattr(ModelDeploymentWorkflows, "slack_training_approval_message_ts")
