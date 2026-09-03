import pytest
from pydantic import ValidationError
from dags.shared.modules.environment.slack import SlackEnvironment

def test_slack_environment_reads_connection_id(monkeypatch):
    monkeypatch.setenv("AIRFLOW_VAR_SLACK_CONNECTION_ID", "slack_conn")
    monkeypatch.setenv("AIRFLOW_VAR_SLACK_CHANNEL_ID", "C123")
    env = SlackEnvironment()
    assert env.SLACK_CONNECTION_ID == "slack_conn"
    assert env.SLACK_CHANNEL_ID == "C123"

def test_slack_environment_missing_connection_id_raises(monkeypatch):
    monkeypatch.delenv("AIRFLOW_VAR_SLACK_CONNECTION_ID", raising=False)
    monkeypatch.setenv("AIRFLOW_VAR_SLACK_CHANNEL_ID", "C123")
    with pytest.raises(ValidationError):
        SlackEnvironment()

def test_slack_environment_module_level_instance():
    from dags.shared.modules.environment.slack import slack_environment
    assert isinstance(slack_environment, SlackEnvironment)
