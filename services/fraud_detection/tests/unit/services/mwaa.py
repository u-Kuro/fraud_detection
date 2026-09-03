import pytest

from services.fraud_detection.src.services.mwaa import trigger_airflow_dag

def test_trigger_airflow_dag_invokes_rest_api(mocker):
    mock_client = mocker.patch("services.fraud_detection.src.services.mwaa.mwaa_client")
    mock_client.invoke_rest_api.return_value = {"RestApiStatusCode": 200, "RestApiResponse": {}}
    trigger_airflow_dag("test_dag", {"key": "value"})
    mock_client.invoke_rest_api.assert_called_once()

def test_trigger_airflow_dag_uses_correct_dag_id(mocker):
    mock_client = mocker.patch("services.fraud_detection.src.services.mwaa.mwaa_client")
    mock_client.invoke_rest_api.return_value = {"RestApiStatusCode": 200, "RestApiResponse": {}}
    trigger_airflow_dag("my_dag", {})
    call_kwargs = mock_client.invoke_rest_api.call_args[1]
    assert "my_dag" in call_kwargs["Path"]

def test_trigger_airflow_dag_raises_on_bad_status(mocker):
    mock_client = mocker.patch("services.fraud_detection.src.services.mwaa.mwaa_client")
    mock_client.invoke_rest_api.return_value = {"RestApiStatusCode": 400, "RestApiResponse": "bad"}
    with pytest.raises(RuntimeError):
        trigger_airflow_dag("test_dag", {})

def test_trigger_airflow_dag_raises_on_5xx_status(mocker):
    mock_client = mocker.patch("services.fraud_detection.src.services.mwaa.mwaa_client")
    mock_client.invoke_rest_api.return_value = {"RestApiStatusCode": 500, "RestApiResponse": "err"}
    with pytest.raises(RuntimeError):
        trigger_airflow_dag("test_dag", {})

def test_trigger_airflow_dag_posts_to_dag_runs_path(mocker):
    mock_client = mocker.patch("services.fraud_detection.src.services.mwaa.mwaa_client")
    mock_client.invoke_rest_api.return_value = {"RestApiStatusCode": 201, "RestApiResponse": {}}
    trigger_airflow_dag("my_dag", {"conf": "val"})
    call_kwargs = mock_client.invoke_rest_api.call_args[1]
    assert call_kwargs["Method"] == "POST"
    assert "dagRuns" in call_kwargs["Path"]
