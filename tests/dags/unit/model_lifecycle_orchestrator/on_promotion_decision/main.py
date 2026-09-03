import dags.model_lifecycle_orchestrator.on_promotion_decision.main as mod

def test_module_is_importable():
    assert mod is not None

def test_on_promotion_decision_callable():
    assert callable(mod.on_promotion_decision)
