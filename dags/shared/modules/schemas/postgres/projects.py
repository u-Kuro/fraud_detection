import uuid
from datetime import datetime

from sqlalchemy import UUID, func, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from dags.shared.modules.schemas.postgres.postgres import PostgresTableBase

class Projects(PostgresTableBase):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    name: Mapped[str] = mapped_column(Text, unique=True)