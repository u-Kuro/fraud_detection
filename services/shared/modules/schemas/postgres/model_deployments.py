import uuid
from datetime import datetime

from sqlalchemy import UUID, func, DateTime, Text, Integer, Boolean, false
from sqlalchemy.orm import Mapped, mapped_column
from services.shared.modules.schemas.postgres.postgres import PostgresTableBase

class ModelDeployments(PostgresTableBase):
    __tablename__ = "model_deployments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    name: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer)
    mlflow_run_id: Mapped[str] = mapped_column(Text)
    dataset_min_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    dataset_max_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    active: Mapped[bool] = mapped_column(Boolean, server_default=false())