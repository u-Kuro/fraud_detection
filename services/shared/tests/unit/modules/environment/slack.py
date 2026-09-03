import pytest
from pydantic import ValidationError

from services.shared.src.modules.environment.slack import SlackEnvironment

def test_slack_environment_reads_all_fields(monkeypatch):
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-token")
    monkeypatch.setenv("SLACK_APP_TOKEN", "xapp-token")
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "secret")
    monkeypatch.setenv("SLACK_CHANNEL_ID", "C123")
    env = SlackEnvironment()
    assert env.SLACK_BOT_TOKEN == "xoxb-token"
    assert env.SLACK_APP_TOKEN == "xapp-token"
    assert env.SLACK_SIGNING_SECRET == "secret"
    assert env.SLACK_CHANNEL_ID == "C123"

def test_slack_environment_missing_bot_token_raises(monkeypatch):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        SlackEnvironment()

def test_slack_environment_missing_app_token_raises(monkeypatch):
    monkeypatch.delenv("SLACK_APP_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        SlackEnvironment()

def test_slack_environment_module_level_instance():
    from services.shared.src.modules.environment.slack import slack_environment
    assert isinstance(slack_environment, SlackEnvironment)

def test_slack_environment_missing_channel_id_raises(monkeypatch):
    monkeypatch.delenv("SLACK_CHANNEL_ID", raising=False)
    with pytest.raises(ValidationError):
        SlackEnvironment()
