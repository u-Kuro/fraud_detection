from pydantic_settings import BaseSettings, SettingsConfigDict

class SlackEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    SLACK_BOT_TOKEN:        str
    SLACK_APP_TOKEN:        str
    SLACK_SIGNING_SECRET:   str
    SLACK_CHANNEL_ID:       str

slack_environment = SlackEnvironment()