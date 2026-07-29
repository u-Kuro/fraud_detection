import uuid
from datetime import datetime

from sqlalchemy import UUID, func, Double, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from services.shared.modules.schemas.postgres.model_deployments import ModelDeployment
from services.shared.modules.schemas.postgres.postgres import PostgresTableBase

class TransactionInference(PostgresTableBase):
    __tablename__ = "transaction_inferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    transaction_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    amount: Mapped[float] = mapped_column(
        Double,
        nullable=False
    )
    is_fraud: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )
    is_fraud_prediction: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )
    is_fraud_probability: Mapped[float | None] = mapped_column(
        Double,
        nullable=True
    )
    model_deployment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(ModelDeployment.id),
        nullable=True
    )
    v1: Mapped[float] = mapped_column(Double, nullable=False)
    v2: Mapped[float] = mapped_column(Double, nullable=False)
    v3: Mapped[float] = mapped_column(Double, nullable=False)
    v4: Mapped[float] = mapped_column(Double, nullable=False)
    v5: Mapped[float] = mapped_column(Double, nullable=False)
    v6: Mapped[float] = mapped_column(Double, nullable=False)
    v7: Mapped[float] = mapped_column(Double, nullable=False)
    v8: Mapped[float] = mapped_column(Double, nullable=False)
    v9: Mapped[float] = mapped_column(Double, nullable=False)
    v10: Mapped[float] = mapped_column(Double, nullable=False)
    v11: Mapped[float] = mapped_column(Double, nullable=False)
    v12: Mapped[float] = mapped_column(Double, nullable=False)
    v13: Mapped[float] = mapped_column(Double, nullable=False)
    v14: Mapped[float] = mapped_column(Double, nullable=False)
    v15: Mapped[float] = mapped_column(Double, nullable=False)
    v16: Mapped[float] = mapped_column(Double, nullable=False)
    v17: Mapped[float] = mapped_column(Double, nullable=False)
    v18: Mapped[float] = mapped_column(Double, nullable=False)
    v19: Mapped[float] = mapped_column(Double, nullable=False)
    v20: Mapped[float] = mapped_column(Double, nullable=False)
    v21: Mapped[float] = mapped_column(Double, nullable=False)
    v22: Mapped[float] = mapped_column(Double, nullable=False)
    v23: Mapped[float] = mapped_column(Double, nullable=False)
    v24: Mapped[float] = mapped_column(Double, nullable=False)
    v25: Mapped[float] = mapped_column(Double, nullable=False)
    v26: Mapped[float] = mapped_column(Double, nullable=False)
    v27: Mapped[float] = mapped_column(Double, nullable=False)
    v28: Mapped[float] = mapped_column(Double, nullable=False)