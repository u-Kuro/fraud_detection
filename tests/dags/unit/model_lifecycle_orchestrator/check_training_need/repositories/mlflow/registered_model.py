import dags.model_lifecycle_orchestrator.check_training_need.repositories.mlflow.registered_model as mod

def test_module_is_importable():
    assert mod is not None

def test_replace_expired_model_exists():
    assert hasattr(mod, "replace_expired_model")

def test_delete_expired_model_exists():
    assert hasattr(mod, "delete_expired_model")
