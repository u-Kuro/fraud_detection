from typing import Optional

from services.fraud_api.src.modules.schemas import TransactionClassification
from services.fraud_api.src.repositories import postgres
from sqlalchemy import text

class FraudInferenceRepository:
    def __init__(self) -> None:
        self.engine = postgres.engine

    def insert(
        self,
        transaction_inference: TransactionClassification,
        is_fraud: Optional[bool] = None,
    ) -> None:
        with self.engine.connect() as connection:
            connection.execute(
                text(f"""
                    WITH active_model AS (
                        SELECT model_id FROM deployed_models
                        WHERE model_name    = :model_name
                          AND model_version = :model_version
                          AND status        = 'active'
                        LIMIT 1
                    )
                    INSERT INTO transaction_inferences(
                        transaction_id,
                        transaction_timestamp,
                        amount,
                        is_fraud,
                        is_fraud_prediction,
                        is_fraud_probability,
                        model_deployment_id,
                        {",".join([f"v{i}" for i in range(1, 29)])}
                    )
                    VALUES(
                        :transaction_id,
                        :transaction_timestamp,
                        :amount,
                        :is_fraud,
                        :is_fraud_prediction,
                        :is_fraud_probability,
                        (SELECT model_id FROM deployed_model),
                        {",".join([f":v{i}" for i in range(1, 29)])}
                    )
                """),
                {
                    **transaction_inference.model_dump(),
                    "is_fraud": (
                        is_fraud
                        if is_fraud is not None
                        else transaction_inference.is_fraud
                    ),
                },
            )
            connection.commit()
