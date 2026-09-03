import dags.model_lifecycle_orchestrator.check_training_need.main as mod

def test_module_is_importable():
    assert mod is not None

def test_check_training_need_callable():
    assert callable(mod.check_training_need)
