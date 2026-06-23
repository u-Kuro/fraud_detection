from shared.schemas import MlflowModelConfig
from shared.schemas.base_environment import MleEnvironmentBase

class TrainingEnvironment(MleEnvironmentBase, MlflowModelConfig):
    """
    Runtime values for training_pipeline.
    Postgres, S3, and MLflow use standard env vars — not declared here.
    """
    SLACK_BOT_USER_AUTH_TOKEN: str
    SLACK_CHANNEL_ID:          str

environment = TrainingEnvironment()