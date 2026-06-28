from pydantic_settings import BaseSettings, SettingsConfigDict

class SlackEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    SLACK_BOT_USER_AUTH_TOKEN: str
    SLACK_APP_LEVEL_TOKEN:     str
    SLACK_CHANNEL_ID:          str
    SLACK_SIGNING_SECRET:      str

slack_environment = SlackEnvironment()