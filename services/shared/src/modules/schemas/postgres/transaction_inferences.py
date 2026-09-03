import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import UUID, func, DateTime, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from services.shared.src.modules.schemas.postgres.postgres import PostgresTableBase

class TransactionInferences(PostgresTableBase):
    __tablename__ = "transaction_inferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    transaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    transaction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    amount: Mapped[float] = mapped_column(Float)
    is_fraud: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_fraud_prediction: Mapped[Optional[bool]] = mapped_column(Boolean)
    is_fraud_probability: Mapped[Optional[float]] = mapped_column(Float)
    model_deployment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    v1: Mapped[float] = mapped_column(Float)
    v2: Mapped[float] = mapped_column(Float)
    v3: Mapped[float] = mapped_column(Float)
    v4: Mapped[float] = mapped_column(Float)
    v5: Mapped[float] = mapped_column(Float)
    v6: Mapped[float] = mapped_column(Float)
    v7: Mapped[float] = mapped_column(Float)
    v8: Mapped[float] = mapped_column(Float)
    v9: Mapped[float] = mapped_column(Float)
    v10: Mapped[float] = mapped_column(Float)
    v11: Mapped[float] = mapped_column(Float)
    v12: Mapped[float] = mapped_column(Float)
    v13: Mapped[float] = mapped_column(Float)
    v14: Mapped[float] = mapped_column(Float)
    v15: Mapped[float] = mapped_column(Float)
    v16: Mapped[float] = mapped_column(Float)
    v17: Mapped[float] = mapped_column(Float)
    v18: Mapped[float] = mapped_column(Float)
    v19: Mapped[float] = mapped_column(Float)
    v20: Mapped[float] = mapped_column(Float)
    v21: Mapped[float] = mapped_column(Float)
    v22: Mapped[float] = mapped_column(Float)
    v23: Mapped[float] = mapped_column(Float)
    v24: Mapped[float] = mapped_column(Float)
    v25: Mapped[float] = mapped_column(Float)
    v26: Mapped[float] = mapped_column(Float)
    v27: Mapped[float] = mapped_column(Float)
    v28: Mapped[float] = mapped_column(Float)