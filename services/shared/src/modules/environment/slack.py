from pydantic import StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class SlackEnvironment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    SLACK_BOT_TOKEN: StrictStr
    SLACK_APP_TOKEN: StrictStr
    SLACK_SIGNING_SECRET: StrictStr
    SLACK_CHANNEL_ID: StrictStr

slack_environment = SlackEnvironment()