import pytest
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from services.shared.src.modules.environment.slack import SlackEnvironment

def test_slack_environment_instance():
    from services.shared.src.modules.environment.slack import slack_environment

    assert isinstance(slack_environment, SlackEnvironment)

def test_slack_environment_values(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv(name="SLACK_BOT_TOKEN", value=value)
    monkeypatch.setenv(name="SLACK_APP_TOKEN", value=value)
    monkeypatch.setenv(name="SLACK_SIGNING_SECRET", value=value)
    monkeypatch.setenv(name="SLACK_CHANNEL_ID", value=value)

    environment = SlackEnvironment()

    assert isinstance(environment.SLACK_BOT_TOKEN, str)
    assert isinstance(environment.SLACK_APP_TOKEN, str)
    assert isinstance(environment.SLACK_SIGNING_SECRET, str)
    assert isinstance(environment.SLACK_CHANNEL_ID, str)

    assert environment.SLACK_BOT_TOKEN == value
    assert environment.SLACK_APP_TOKEN == value
    assert environment.SLACK_SIGNING_SECRET == value
    assert environment.SLACK_CHANNEL_ID == value

def test_slack_environment_failure_with_missing_environment(monkeypatch: MonkeyPatch):
    monkeypatch.delenv(
        name="SLACK_BOT_TOKEN",
        raising=False
    )

    with pytest.raises(ValidationError):
        SlackEnvironment()