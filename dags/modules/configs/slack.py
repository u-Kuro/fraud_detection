from pydantic import BaseModel, ConfigDict

class SlackConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    SLACK_CONNECTION_ID: str = "slack"

slack_config = SlackConfig()
