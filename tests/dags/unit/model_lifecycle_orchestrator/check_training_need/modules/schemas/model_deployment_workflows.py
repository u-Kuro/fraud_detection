from dags.model_lifecycle_orchestrator.check_training_need.modules.schemas.model_deployment_workflows import ModelDeploymentWorkflow

def test_model_deployment_workflow_field_keys_default():
    keys = ModelDeploymentWorkflow.model_field_keys()
    assert "id" in keys
    assert "state" in keys
    assert "slack_training_approval_message_ts" in keys

def test_model_deployment_workflow_field_keys_with_rename():
    keys = ModelDeploymentWorkflow.model_field_keys(rename={"id": "workflow_id"})
    assert "workflow_id" in keys
    assert "id" not in keys

def test_model_deployment_workflow_field_keys_preserves_order():
    keys = ModelDeploymentWorkflow.model_field_keys()
    assert isinstance(keys, list)
    assert len(keys) == 3

def test_model_deployment_workflow_field_keys_with_empty_rename():
    keys_no_rename = ModelDeploymentWorkflow.model_field_keys()
    keys_empty_rename = ModelDeploymentWorkflow.model_field_keys(rename={})
    assert keys_no_rename == keys_empty_rename
