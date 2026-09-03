import dags.model_lifecycle_orchestrator.check_training_need.repositories.mlflow.run as mod

def test_module_is_importable():
    assert mod is not None

def test_delete_expired_mlflow_run_exists():
    assert hasattr(mod, "delete_expired_mlflow_run")
