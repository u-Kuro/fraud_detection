from pydantic import BaseModel, ConfigDict

class SlackConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    SLACK_CONNECTION_ID: str = "mle_slack"

slack_config = SlackConfig()
