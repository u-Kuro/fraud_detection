from sqlalchemy import Column, func, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID

from services.shared.modules.schemas.postgres.postgres import PostgresTableBase

class Projects(PostgresTableBase):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    name = Column(Text, nullable=False, unique=True)