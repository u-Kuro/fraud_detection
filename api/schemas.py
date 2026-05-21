"""
api/schemas.py — Input/Output validation schemas

Pydantic does two things here:
  1. Validates input before it reaches the model (prevents cryptic sklearn errors)
  2. Auto-generates the /docs Swagger UI with examples
"""
from datetime import datetime, timezone
from typing import Annotated, cast, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator, UUID4
from pydantic_settings import BaseSettings, SettingsConfigDict

class MlflowModelUri(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    model_uri: Union[
        Annotated[str, Field(
            pattern=r"^models:/[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+$",
            description="Format: models:/name@alias"
        )],
        Annotated[str, Field(
            pattern=r"^models:/[a-zA-Z0-9_-]+/\d+$",
            description="Format: models:/name/version"
        )]
    ]

class MlflowModelFlavor(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    flavor: Literal["sklearn", "pyfunc"] = Field(..., description="Type of MLflow model")

class MlflowModelFeatures(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    transaction_timestamp: datetime = Field(..., strict=False, description="Transaction timestamp in UTC")
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
    is_fraud: Optional[bool] = Field(None, description="Fraud label for transaction")

class MlflowModelDataset(MlflowModelFeatures, MlflowModelLabels):
    model_config = ConfigDict(strict=True, extra="forbid")

class PredictionRequest(MlflowModelFeatures):
    model_config = ConfigDict(strict=True, extra="forbid")
    transaction_id: UUID4 = Field(..., strict=False, description="Transaction ID")

class PredictionResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    is_fraud_prediction: bool = Field(..., description="Fraud prediction for transaction")
    is_fraud_probability: float = Field(..., ge=0.0, le=1.0)

class DeployedModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    model_name: str = Field(..., description="Name of model used for inference")
    model_version: int = Field(..., description="Version of model used for inference")

class TransactionInference(PredictionRequest, PredictionResponse, MlflowModelLabels, DeployedModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    latency_ms: float = Field(..., description="Inference time")

class Environment(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    FRAUD_DETECTION_DB: str
    MLFLOW_TRACKING_URI: str
    MLFLOW_MODEL_URI: str
    MLFLOW_MODEL_FLAVOR: str

    @property
    def mlflow_model_uri(self) -> MlflowModelUri:
        return MlflowModelUri(model_uri=self.MLFLOW_MODEL_URI)

    @property
    def mlflow_model_flavor(self) -> MlflowModelFlavor:
        return MlflowModelFlavor(flavor=cast(Literal["sklearn", "pyfunc"], self.MLFLOW_MODEL_FLAVOR))