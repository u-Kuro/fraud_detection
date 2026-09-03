import dags.model_lifecycle_orchestrator.on_promotion_decision.repositories.postgres.model_deployment_workflows as mod

def test_module_is_importable():
    assert mod is not None

def test_update_approved_promotion_workflow_exists():
    assert hasattr(mod, "update_approved_promotion_workflow")

def test_delete_rejected_promotion_workflow_exists():
    assert hasattr(mod, "delete_rejected_promotion_workflow")
