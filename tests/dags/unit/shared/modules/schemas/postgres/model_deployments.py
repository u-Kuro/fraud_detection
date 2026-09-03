from dags.shared.modules.schemas.postgres.model_deployments import ModelDeployments

def test_model_deployments_tablename():
    assert ModelDeployments.__tablename__ == "model_deployments"

def test_model_deployments_has_active():
    assert hasattr(ModelDeployments, "active")

def test_model_deployments_has_mlflow_run_id():
    assert hasattr(ModelDeployments, "mlflow_run_id")

def test_model_deployments_has_version():
    assert hasattr(ModelDeployments, "version")
