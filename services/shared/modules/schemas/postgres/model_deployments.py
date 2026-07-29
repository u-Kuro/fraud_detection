import uuid
from datetime import datetime

from sqlalchemy import UUID, func, ForeignKey, Text, Integer, Boolean, false, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from services.shared.modules.schemas.postgres.postgres import PostgresTableBase
from services.shared.modules.schemas.postgres.projects import Project

class ModelDeployment(PostgresTableBase):
    __tablename__ = "model_deployments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(Project.id),
        nullable=False
    )
    name: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    mlflow_run_id: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    dataset_min_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    dataset_max_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=false()
    )

