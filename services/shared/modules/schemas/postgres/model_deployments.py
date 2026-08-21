from sqlalchemy import Column, func, DateTime, Text, Integer, Boolean, false
from sqlalchemy.dialects.postgresql import UUID

from services.shared.modules.schemas.postgres.postgres import PostgresTableBase

class ModelDeployments(PostgresTableBase):
    __tablename__ = "model_deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    project_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    mlflow_run_id = Column(Text, nullable=False)
    dataset_min_timestamp = Column(DateTime(timezone=True), nullable=False)
    dataset_max_timestamp = Column(DateTime(timezone=True), nullable=False)
    active = Column(Boolean, nullable=False, server_default=false())