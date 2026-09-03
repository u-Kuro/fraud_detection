import dags.model_lifecycle_orchestrator.check_training_need.repositories.postgres.model_deployments as mod

def test_module_is_importable():
    assert mod is not None

def test_get_active_model_deployment_exists():
    assert hasattr(mod, "get_active_model_deployment")

def test_has_active_model_deployment_exists():
    assert hasattr(mod, "has_active_model_deployment")
