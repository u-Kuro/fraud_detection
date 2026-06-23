from pydantic_settings import BaseSettings, SettingsConfigDict


class MleEnvironmentBase(BaseSettings):
    """
    Shared base for all MLE service environments.

    S3_BUCKET is the only field because every other connectivity value
    (PGHOST, AWS_DEFAULT_REGION, MLFLOW_TRACKING_URI …) is consumed directly
    by its library from standard env vars — no Python schema entry needed.
    S3_BUCKET has no standard boto3 env var equivalent, so we declare it here
    with a default matching the known bucket name.
    """
    model_config = SettingsConfigDict(case_sensitive=True)

    S3_MLE_BUCKET: str = "mle"