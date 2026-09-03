from services.shared.src.modules.schemas.postgres.model_deployments import ModelDeployments

def test_model_deployments_tablename():
    assert ModelDeployments.__tablename__ == "model_deployments"

def test_model_deployments_has_id():
    assert hasattr(ModelDeployments, "id")

def test_model_deployments_has_project_id():
    assert hasattr(ModelDeployments, "project_id")

def test_model_deployments_has_name():
    assert hasattr(ModelDeployments, "name")

def test_model_deployments_has_version():
    assert hasattr(ModelDeployments, "version")

def test_model_deployments_has_mlflow_run_id():
    assert hasattr(ModelDeployments, "mlflow_run_id")

def test_model_deployments_has_dataset_min_timestamp():
    assert hasattr(ModelDeployments, "dataset_min_timestamp")

def test_model_deployments_has_dataset_max_timestamp():
    assert hasattr(ModelDeployments, "dataset_max_timestamp")

def test_model_deployments_has_active():
    assert hasattr(ModelDeployments, "active")

def test_model_deployments_active_default_false():
    col = ModelDeployments.active.property.columns[0]
    # server_default is false()
    assert col.server_default is not None
