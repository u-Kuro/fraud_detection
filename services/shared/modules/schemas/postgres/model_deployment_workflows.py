import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional

from sqlalchemy import UUID, func, DateTime, Enum, Boolean, false, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from services.shared.modules.schemas.postgres.postgres import PostgresTableBase

@dataclass(frozen=True)
class ModelDeploymentWorkflowState(StrEnum):
    train_pending = "train_pending"
    promote_pending = "promote_pending"
    reserved = "reserved"

class ModelDeploymentWorkflows(PostgresTableBase):
    __tablename__ = "model_deployment_workflows"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    state: Mapped[ModelDeploymentWorkflowState] = mapped_column(
        Enum(
            ModelDeploymentWorkflowState,
            native_enum=False,
            create_constraint=True,
            name="state_check",
        )
    )
    training_approved: Mapped[bool] = mapped_column(Boolean, server_default=false())
    promotion_approved: Mapped[bool] = mapped_column(Boolean, server_default=false())
    model_trained_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    mlflow_run_id: Mapped[Optional[str]] = mapped_column(Text)
    registered_model_name: Mapped[Optional[str]] = mapped_column(Text)
    registered_model_version: Mapped[Optional[int]] = mapped_column(Integer)
    model_dataset_min_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    model_dataset_max_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    training_approval_slack_ts: Mapped[str] = mapped_column(Text)
    promotion_approval_slack_ts: Mapped[Optional[str]] = mapped_column(Text)