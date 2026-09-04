import pytest
from _pytest.monkeypatch import MonkeyPatch
from pydantic import ValidationError

from services.shared.src.modules.environment.slack import SlackEnvironment

def test_slack_environment_bot_token_value(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv("SLACK_BOT_TOKEN", value)

    from services.shared.src.modules.environment.slack import slack_environment

    assert slack_environment.SLACK_BOT_TOKEN == value

def test_slack_environment_app_token_value(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv("SLACK_APP_TOKEN", value)

    from services.shared.src.modules.environment.slack import slack_environment

    assert slack_environment.SLACK_APP_TOKEN == value

def test_slack_environment_signing_secret_value(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv("SLACK_SIGNING_SECRET", value)

    from services.shared.src.modules.environment.slack import slack_environment

    assert slack_environment.SLACK_SIGNING_SECRET == value

def test_slack_environment_channel_id_value(monkeypatch: MonkeyPatch):
    value = "value"
    monkeypatch.setenv("SLACK_CHANNEL_ID", value)

    from services.shared.src.modules.environment.slack import slack_environment

    assert slack_environment.SLACK_CHANNEL_ID == value

def test_slack_environment_with_missing_environment(monkeypatch: MonkeyPatch):
    monkeypatch.delenv("SLACK_BOT_TOKEN", raising=False)

    with pytest.raises(ValidationError):
        SlackEnvironment()