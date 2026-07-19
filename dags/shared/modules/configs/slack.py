from dataclasses import dataclass

@dataclass(frozen=True)
class SlackConfig:
    SLACK_CONNECTION_ID: str = "mle_slack"
