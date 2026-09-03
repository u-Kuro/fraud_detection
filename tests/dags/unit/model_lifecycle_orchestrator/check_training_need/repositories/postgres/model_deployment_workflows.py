import dags.model_lifecycle_orchestrator.check_training_need.repositories.postgres.model_deployment_workflows as mod

def test_module_is_importable():
    assert mod is not None

def test_get_expired_model_deployment_workflow_exists():
    assert hasattr(mod, "get_expired_model_deployment_workflow_with_its_replacement")

def test_has_expired_promote_pending_workflow_with_replacement_exists():
    assert hasattr(mod, "has_expired_promote_pending_workflow_with_replacement")

def test_delete_expired_promote_pending_workflow_exists():
    assert hasattr(mod, "delete_expired_promote_pending_workflow")

def test_initialize_train_pending_workflow_exists():
    assert hasattr(mod, "initialize_train_pending_workflow")

def test_update_train_pending_workflow_exists():
    assert hasattr(mod, "update_train_pending_workflow")

def test_get_current_model_deployment_workflow_for_training_exists():
    assert hasattr(mod, "get_current_model_deployment_workflow_for_training")
