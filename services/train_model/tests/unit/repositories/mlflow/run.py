import pytest
from unittest.mock import MagicMock, patch


def test_transactional_mlflow_run_is_context_manager(mocker):
    mock_module = mocker.patch(
        "services.train_model.src.repositories.mlflow.run.mlflow_module"
    )
    mock_run = MagicMock()
    mock_run.info.run_id = "run-abc"
    mock_module.start_run.return_value.__enter__ = MagicMock(return_value=mock_run)
    mock_module.start_run.return_value.__exit__ = MagicMock(return_value=False)

    from services.train_model.src.repositories.mlflow.run import transactional_mlflow_run
    with transactional_mlflow_run(run_name="test_run"):
        pass  # no exception → success path

    mock_module.start_run.assert_called_once_with(run_name="test_run")


def test_transactional_mlflow_run_deletes_run_on_exception(mocker):
    mock_client = mocker.patch(
        "services.train_model.src.repositories.mlflow.run.mlflow_client"
    )
    mock_module = mocker.patch(
        "services.train_model.src.repositories.mlflow.run.mlflow_module"
    )
    mock_run = MagicMock()
    mock_run.info.run_id = "run-err"
    mock_module.start_run.return_value.__enter__ = MagicMock(return_value=mock_run)
    mock_module.start_run.return_value.__exit__ = MagicMock(return_value=False)
    mock_client.search_model_versions.return_value = []

    from services.train_model.src.repositories.mlflow.run import transactional_mlflow_run
    with pytest.raises(RuntimeError):
        with transactional_mlflow_run(run_name="fail_run"):
            raise ValueError("inner error")

    mock_client.delete_run.assert_called_once_with(run_id="run-err")


def test_transactional_mlflow_run_raises_runtime_error_on_failure(mocker):
    mock_client = mocker.patch(
        "services.train_model.src.repositories.mlflow.run.mlflow_client"
    )
    mock_module = mocker.patch(
        "services.train_model.src.repositories.mlflow.run.mlflow_module"
    )
    mock_run = MagicMock()
    mock_run.info.run_id = "run-xyz"
    mock_module.start_run.return_value.__enter__ = MagicMock(return_value=mock_run)
    mock_module.start_run.return_value.__exit__ = MagicMock(return_value=False)
    mock_client.search_model_versions.return_value = []

    from services.train_model.src.repositories.mlflow.run import transactional_mlflow_run
    with pytest.raises(RuntimeError, match="Model training failed"):
        with transactional_mlflow_run(run_name="bad_run"):
            raise Exception("anything")


def test_save_model_hyperparameters_calls_log_params(mocker):
    mock_module = mocker.patch(
        "services.train_model.src.repositories.mlflow.run.mlflow_module"
    )
    from services.train_model.src.repositories.mlflow.run import save_model_hyperparameters
    save_model_hyperparameters(
        mlflow_model_run_id="run-abc",
        model_hyperparameters={"lr": 0.1, "depth": 5},
    )
    mock_module.log_params.assert_called_once()


def test_save_model_metrics_calls_log_metrics(mocker):
    mock_module = mocker.patch(
        "services.train_model.src.repositories.mlflow.run.mlflow_module"
    )
    mocker.patch(
        "services.train_model.src.repositories.mlflow.run.save_model_metric_figures"
    )
    from services.train_model.src.repositories.mlflow.run import save_model_metrics
    save_model_metrics(
        mlflow_model_run_id="run-abc",
        mlflow_model_id="model-123",
        model_metrics={"f1": 0.8, "roc_auc": 0.9},
        model_metric_figures={},
    )
    mock_module.log_metrics.assert_called_once()


def test_save_model_metric_figures_calls_log_figure(mocker):
    mock_module = mocker.patch(
        "services.train_model.src.repositories.mlflow.run.mlflow_module"
    )
    from unittest.mock import MagicMock
    from matplotlib.figure import Figure

    fig = MagicMock(spec=Figure)
    from services.train_model.src.repositories.mlflow.run import save_model_metric_figures
    save_model_metric_figures({"confusion_matrix": fig, "probability_scatter": fig})
    assert mock_module.log_figure.call_count == 2


def test_save_model_metric_figures_empty_dict(mocker):
    mock_module = mocker.patch(
        "services.train_model.src.repositories.mlflow.run.mlflow_module"
    )
    from services.train_model.src.repositories.mlflow.run import save_model_metric_figures
    save_model_metric_figures({})
    mock_module.log_figure.assert_not_called()
