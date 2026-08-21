from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy import Column, func, DateTime, Enum, Boolean, false, Text, Integer
from sqlalchemy.dialects.postgresql import UUID

from services.shared.modules.schemas.postgres.postgres import PostgresTableBase

@dataclass(frozen=True)
class ModelDeploymentWorkflowState(StrEnum):
    train_pending = "train_pending"
    promote_pending = "promote_pending"
    promote_pending_replacement = "promote_pending_replacement"

class ModelDeploymentWorkflows(PostgresTableBase):
    __tablename__ = "model_deployment_workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    project_id = Column(UUID(as_uuid=True), nullable=False)
    state = Column(
        Enum(
            ModelDeploymentWorkflowState,
            native_enum=False,
            create_constraint=True,
            name="state_check"
        ),
        nullable=False
    )
    training_approved = Column(Boolean, nullable=False, server_default=false())
    promotion_approved = Column(Boolean, nullable=False, server_default=false())
    model_trained_at = Column(DateTime(timezone=True), nullable=False)
    mlflow_run_id = Column(Text, nullable=True)
    registered_model_name = Column(Text, nullable=True)
    registered_model_version = Column(Integer, nullable=True)
    model_dataset_min_timestamp = Column(DateTime(timezone=True), nullable=True)
    model_dataset_max_timestamp = Column(DateTime(timezone=True), nullable=True)
    training_approval_slack_ts = Column(Text, nullable=False)
    promotion_approval_slack_ts = Column(Text, nullable=True)