import dags.model_lifecycle_orchestrator.on_training_decision.repositories.postgres.model_deployment_workflows as mod

def test_module_is_importable():
    assert mod is not None

def test_update_approved_training_workflow_exists():
    assert hasattr(mod, "update_approved_training_workflow")

def test_delete_rejected_training_workflow_exists():
    assert hasattr(mod, "delete_rejected_training_workflow")

def test_update_trained_model_info_in_workflow_exists():
    assert hasattr(mod, "update_trained_model_info_in_workflow")

def test_update_promotion_pending_workflow_exists():
    assert hasattr(mod, "update_promotion_pending_workflow")
