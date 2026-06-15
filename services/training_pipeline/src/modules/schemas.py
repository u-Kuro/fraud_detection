from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    # Postgres
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    FRAUD_DETECTION_DB_NAME: str

    # S3
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_MODEL_DATASETS_BUCKET: str = "model-datasets"

    # MLflow
    MLFLOW_TRACKING_URI: str
    MLFLOW_EXPERIMENT_NAME: str = "fraud-detection"

    # Slack
    SLACK_WEBHOOK_URL: str

    # Training hyperparams
    MAX_SELECTED_ROWS: int = 100_000
    TRAINING_MINIMUM_ROWS: int = 1_000
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    VAL_SIZE: float = 0.2
    BAYES_STEPS: int = 30
    TRAINING_TIMEOUT_SECONDS: int = 3600

environment = Environment()
