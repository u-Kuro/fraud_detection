import dags.model_lifecycle_orchestrator.check_training_need.services.tasks as mod

def test_module_is_importable():
    assert mod is not None

def test_no_action_exists():
    assert hasattr(mod, "no_action")

def test_drift_check_operator_exists():
    assert hasattr(mod, "drift_check_operator")

def test_invalidate_expired_challenger_model_exists():
    assert hasattr(mod, "invalidate_expired_challenger_model")
