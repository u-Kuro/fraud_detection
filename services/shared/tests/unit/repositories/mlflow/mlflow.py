def test_initialize_mlflow_sets_workspace(mocker):
    mock_mlflow = mocker.patch("services.shared.repositories.mlflow.mlflow.mlflow")
    mock_env = mocker.patch("services.shared.repositories.mlflow.mlflow.mlflow_environment")
    mock_env.MLFLOW_WORKSPACE = "test_ws"

    from services.shared.src.repositories.mlflow.mlflow import initialize_mlflow
    initialize_mlflow()

    mock_mlflow.set_workspace.assert_called_once_with("test_ws")

def test_initialize_mlflow_sets_experiment(mocker):
    mock_mlflow = mocker.patch("services.shared.repositories.mlflow.mlflow.mlflow")
    mocker.patch("services.shared.repositories.mlflow.mlflow.mlflow_environment")

    from services.shared.src.repositories.mlflow.mlflow import initialize_mlflow
    initialize_mlflow()

    mock_mlflow.set_experiment.assert_called_once_with("fraud_detection")

def test_get_mlflow_client_returns_client(mocker):
    mocker.patch("services.shared.repositories.mlflow.mlflow.mlflow")

    from services.shared.src.repositories.mlflow.mlflow import get_mlflow_client
    from mlflow import MlflowClient
    client = get_mlflow_client()
    assert isinstance(client, MlflowClient)

def test_get_mlflow_returns_mlflow_module(mocker):
    mock_mlflow = mocker.patch("services.shared.repositories.mlflow.mlflow.mlflow")

    from services.shared.src.repositories.mlflow.mlflow import get_mlflow
    result = get_mlflow()
    assert result is mock_mlflow

def test_module_level_client_exists():
    from services.shared.src.repositories.mlflow.mlflow import mlflow_client
    assert mlflow_client is not None

def test_module_level_mlflow_module_exists():
    from services.shared.src.repositories.mlflow.mlflow import mlflow_module
    assert mlflow_module is not None
