from typing import Literal, Optional, Protocol, runtime_checkable
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


@runtime_checkable
class OtelEnvironment(Protocol):
    OTEL_ENABLED: bool
    OTEL_SERVICE_NAME: str
    OTEL_SERVICE_VERSION: str
    OTEL_DEPLOYMENT_ENVIRONMENT: str
    OTEL_URL: str
    OTEL_METRIC_EXPORT_INTERVAL_MS: int


class PipelineStateRow(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    state: Literal["drift_pending", "train_pending", "promoting"]
    drift_approved: bool = False
    run_id: Optional[str] = None
    model_version: Optional[int] = None
    dataset_min_date: Optional[datetime] = None
    dataset_max_date: Optional[datetime] = None
    slack_message_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeployedModelRow(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    model_id: int
    model_name: str
    model_version: int
    dataset_min_date: Optional[datetime] = None
    dataset_max_date: datetime
    status: Literal["promoting", "active"]
    promoted_at: datetime


class ArchivingBatchResult(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    batch_number: int = Field(..., ge=1)
    rows_read: int = Field(..., ge=0)
    rows_deleted: int = Field(..., ge=0)
    parquet_key: str
    cutoff_timestamp: datetime
    elapsed_ms: float = Field(..., ge=0.0)


# from datetime import datetime, timezone
# from typing import Annotated, Literal, Optional, Union
#
# from pydantic import BaseModel, ConfigDict, Field, field_validator, UUID4
#
# class MlflowModelUri(BaseModel):
#     model_config = ConfigDict(strict=True, extra="forbid")
#     model_uri: Union[
#         Annotated[
#             str,
#             Field(
#                 pattern=r"^models:/[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+$",
#                 description="Format: models:/name@alias",
#             ),
#         ],
#         Annotated[
#             str,
#             Field(
#                 pattern=r"^models:/[a-zA-Z0-9_-]+/\d+$",
#                 description="Format: models:/name/version",
#             ),
#         ],
#     ]
#
# class MlflowModelFlavor(BaseModel):
#     model_config = ConfigDict(strict=True, extra="forbid")
#     flavor: Literal["sklearn", "pyfunc"] = Field(
#         ..., description="Type of MLflow model"
#     )
#
#
#
# class MlflowModelLabels(BaseModel):
#     model_config = ConfigDict(strict=True, extra="forbid")
#     is_fraud: Optional[bool] = Field(None, description="Fraud label for transaction")
#
# class MlflowModelDataset(MlflowModelFeatures, MlflowModelLabels):
#     model_config = ConfigDict(strict=True, extra="forbid")
#
# class ClassificationRequest(MlflowModelFeatures):
#     model_config = ConfigDict(strict=True, extra="forbid")
#     transaction_id: UUID4 = Field(..., strict=False, description="Transaction ID")
#
# class ClassificationResponse(BaseModel):
#     model_config = ConfigDict(strict=True, extra="forbid")
#     is_fraud_prediction: bool = Field(
#         ..., description="Fraud prediction for transaction"
#     )
#     is_fraud_probability: float = Field(..., ge=0.0, le=1.0)
#
# class DeployedModel(BaseModel):
#     model_config = ConfigDict(strict=True, extra="forbid")
#     model_name: str = Field(..., description="Name of model used for inference")
#     model_version: int = Field(..., description="Version of model used for inference")
#
# class TransactionClassification(
#     ClassificationRequest, ClassificationResponse, MlflowModelLabels, DeployedModel
# ):
#     model_config = ConfigDict(strict=True, extra="forbid")
#
# class ApiConfig(BaseModel):
#     model_name: str = "fraud-detector"
#     model_alias: str = "champion"
#     prediction_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
#     max_latency_ms: float = Field(default=500.0, gt=0.0)
#
# class DriftUpdateResponse(BaseModel):
#     status: str
#     fraud_api_drift_share: float = Field(ge=0.0, le=1.0)
#
# class HealthResponse(BaseModel):
#     status: str
#     model_loaded: bool
#
# class SeaweedFSConfig(BaseModel):
#     model_config = ConfigDict(strict=True, extra="forbid")
#     endpoint: str
#     access_key: str = "any"
#     secret_key: str = "any"
#     bucket: str = "mlflow-artifacts"
#
# class ArchivingBatchResult(BaseModel):
#     model_config = ConfigDict(strict=True, extra="forbid")
#     batch_number: int = Field(..., ge=1)
#     rows_read: int = Field(..., ge=0)
#     rows_deleted: int = Field(..., ge=0)
#     parquet_key: str
#     cutoff_timestamp: datetime
#     elapsed_ms: float = Field(..., ge=0.0)
#
# class ModelTrainingCutoff(BaseModel):
#     model_config = ConfigDict(strict=True, extra="forbid")
#     metadata_id: int
#     model_name: str
#     training_timestamp: datetime
#     data_start_timestamp: datetime
#     data_end_timestamp: datetime
