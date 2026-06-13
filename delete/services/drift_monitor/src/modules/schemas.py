from pydantic_settings import BaseSettings, SettingsConfigDict

class Environment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    # Postgres
    FRAUD_DETECTION_DB_NAME: str

    # SeaweedFS / S3
    SEAWEEDFS_S3_URL: str
    SEAWEEDFS_ACCESS_KEY: str
    SEAWEEDFS_SECRET_KEY: str
    SEAWEEDFS_TRAINED_MODEL_DATASET_BUCKET: str
    SEAWEEDFS_DRIFT_REPORTS_BUCKET: str

    # Slack
    SLACK_WEBHOOK_URL: str
    SLACK_CHANNEL: str = "#ml-alerts"
    SLACK_BOT_USER_AUTH_TOKEN: str
    SLACK_CHANNEL_ID: str

    # Argo Workflows (used to submit training when approved)
    ARGO_SERVER_URL: str = "http://argo-workflows-server:2746"
    ARGO_WORKFLOW_TEMPLATE_NAME: str = "training-pipeline"
    ARGO_NAMESPACE: str = "ml-pipeline"
    ARGO_TOKEN: str = ""  # SA token; empty in-cluster uses projected SA

    # Drift thresholds
    MAX_SELECTED_ROWS: int = 50_000
    DRIFT_THRESHOLD: float = 0.5
    MINIMUM_ROWS: int = 500
    LOOKBACK_DAYS: int = 7

    # OTel
    OTEL_ENABLED: bool = False
    OTEL_SERVICE_NAME: str = "drift_monitor"
    OTEL_SERVICE_VERSION: str = "0.1.0"
    OTEL_DEPLOYMENT_ENVIRONMENT: str = "development"
    OTEL_URL: str = "http://otel_collector:4317"
    OTEL_METRIC_EXPORT_INTERVAL_MS: int = 60_000

    @property
    def postgres_fraud_database_url(self) -> str:
        return f"postgresql:///${self.FRAUD_DETECTION_DB_NAME}"