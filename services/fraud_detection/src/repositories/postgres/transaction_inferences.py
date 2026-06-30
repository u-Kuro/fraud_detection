from sqlalchemy import text

from services.fraud_detection.src.modules.schemas import FraudClassificationOutput
from services.fraud_detection.src.repositories.postgres import engine

def insert_transaction_inference(
    transaction_inference: FraudClassificationOutput,
    is_fraud: bool | None = None,
):
    with engine.connect() as connection:
        connection.execute(
            text(f"""
                WITH active_model AS (
                    SELECT model_id FROM model_deployments
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
                    (SELECT model_id FROM active_model),
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