from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    # Postgres
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    FRAUD_DETECTION_DB_NAME: str

    # SeaweedFS
    SEAWEEDFS_S3_URL: str
    SEAWEEDFS_ACCESS_KEY: str
    SEAWEEDFS_SECRET_KEY: str
    SEAWEEDFS_DRIFT_REFERENCE_BUCKET: str = "drift-reference"
    SEAWEEDFS_MODEL_DATASETS_BUCKET: str = "model-datasets"

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

    # OTel
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "training_pipeline"
    OTEL_SERVICE_VERSION: str = "0.1.0"
    OTEL_DEPLOYMENT_ENVIRONMENT: str = "development"
    OTEL_URL: str = "http://otel_collector:4317"
    OTEL_METRIC_EXPORT_INTERVAL_MS: int = 60_000


environment = Environment()
