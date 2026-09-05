from _pytest.monkeypatch import MonkeyPatch

from services.shared.src.modules.environment.slack import SlackEnvironment

class TestSlackEnvironment:
    def test_instance(self):
        from services.shared.src.modules.environment.slack import slack_environment

        assert isinstance(slack_environment, SlackEnvironment)

    def test_values(self, monkeypatch: MonkeyPatch):
        value = "value"
        monkeypatch.setenv(name="SLACK_BOT_TOKEN", value=value)
        monkeypatch.setenv(name="SLACK_APP_TOKEN", value=value)
        monkeypatch.setenv(name="SLACK_SIGNING_SECRET", value=value)
        monkeypatch.setenv(name="SLACK_CHANNEL_ID", value=value)

        environment = SlackEnvironment()

        assert environment.SLACK_BOT_TOKEN == value
        assert environment.SLACK_APP_TOKEN == value
        assert environment.SLACK_SIGNING_SECRET == value
        assert environment.SLACK_CHANNEL_ID == value