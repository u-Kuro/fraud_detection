from datetime import datetime, timezone
from typing import Annotated, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator, UUID4
from pydantic_settings import BaseSettings, SettingsConfigDict

class MlflowModelUri(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    model_uri: Union[
        Annotated[str, Field(pattern=r"^models:/[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+$")],
        Annotated[str, Field(pattern=r"^models:/[a-zA-Z0-9_-]+/\d+$")],
    ]

class MlflowModelFeatures(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    transaction_timestamp: datetime = Field(
        ..., strict=False, description="Transaction timestamp in UTC"
    )

    @field_validator("transaction_timestamp")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        return v.astimezone(timezone.utc)

    amount: float = Field(..., description="Transaction amount in USD")
    v1: float = Field(..., description="PCA feature v1")
    v2: float = Field(..., description="PCA feature v2")
    v3: float = Field(..., description="PCA feature v3")
    v4: float = Field(..., description="PCA feature v4")
    v5: float = Field(..., description="PCA feature v5")
    v6: float = Field(..., description="PCA feature v6")
    v7: float = Field(..., description="PCA feature v7")
    v8: float = Field(..., description="PCA feature v8")
    v9: float = Field(..., description="PCA feature v9")
    v10: float = Field(..., description="PCA feature v10")
    v11: float = Field(..., description="PCA feature v11")
    v12: float = Field(..., description="PCA feature v12")
    v13: float = Field(..., description="PCA feature v13")
    v14: float = Field(..., description="PCA feature v14")
    v15: float = Field(..., description="PCA feature v15")
    v16: float = Field(..., description="PCA feature v16")
    v17: float = Field(..., description="PCA feature v17")
    v18: float = Field(..., description="PCA feature v18")
    v19: float = Field(..., description="PCA feature v19")
    v20: float = Field(..., description="PCA feature v20")
    v21: float = Field(..., description="PCA feature v21")
    v22: float = Field(..., description="PCA feature v22")
    v23: float = Field(..., description="PCA feature v23")
    v24: float = Field(..., description="PCA feature v24")
    v25: float = Field(..., description="PCA feature v25")
    v26: float = Field(..., description="PCA feature v26")
    v27: float = Field(..., description="PCA feature v27")
    v28: float = Field(..., description="PCA feature v28")

class MlflowModelLabels(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    is_fraud: Optional[bool] = None

class MlflowModelDataset(MlflowModelFeatures, MlflowModelLabels):
    model_config = ConfigDict(strict=True, extra="forbid")

class TransactionDetails(MlflowModelFeatures):
    model_config = ConfigDict(strict=True, extra="forbid")
    transaction_id: UUID4 = Field(..., strict=False)

class ClassificationResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    is_fraud_prediction: bool
    is_fraud_probability: float = Field(..., ge=0.0, le=1.0)

class DeployedModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    model_name: str
    model_version: int

class TransactionClassification(TransactionDetails, ClassificationResponse, MlflowModelLabels, DeployedModel):
    model_config = ConfigDict(strict=True, extra="forbid")

class ApiConfig(BaseModel):
    model_name: str = "fraud-detector"
    model_alias: str = "champion"
    prediction_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    max_latency_ms: float = Field(default=500.0, gt=0.0)

class DriftUpdateResponse(BaseModel):
    status: str
    share_drifted_features: float = Field(ge=0.0, le=1.0)

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

class Environment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)
    FRAUD_DETECTION_DB_NAME: str
    MLFLOW_TRACKING_URI: str
    MLFLOW_MODEL_URI: str
    SLACK_BOT_USER_AUTH_TOKEN: str
    SLACK_APP_LEVEL_TOKEN: str
    SLACK_CHANNEL_ID: str
    SLACK_SIGNING_SECRET: str

    @property
    def postgres_fraud_database_url(self) -> str:
        return f"postgresql:///${self.FRAUD_DETECTION_DB_NAME}"

    @property
    def mlflow_model_uri(self) -> MlflowModelUri:
        return MlflowModelUri(model_uri=self.MLFLOW_MODEL_URI)