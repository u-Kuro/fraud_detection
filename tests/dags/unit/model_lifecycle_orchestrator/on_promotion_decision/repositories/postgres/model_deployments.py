import dags.model_lifecycle_orchestrator.on_promotion_decision.repositories.postgres.model_deployments as mod

def test_module_is_importable():
    assert mod is not None

def test_promote_model_deployment_exists():
    assert hasattr(mod, "promote_model_deployment")
