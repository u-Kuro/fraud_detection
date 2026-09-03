import dags.model_lifecycle_orchestrator.on_training_decision.modules.configs.airflow.xcom as mod

def test_module_is_importable():
    assert mod is not None
