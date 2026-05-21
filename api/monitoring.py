"""
api/monitoring.py — Inference logging to Postgres

Architecture:
  1. InferenceLogger (this file) — called per-request, writes one row to
     the inference_logs Postgres table. Fast, minimal, never fails loudly.

  2. scripts/drift_report.py    — run separately (daily/weekly), reads the
     inference_logs table, compares to training data, and generates an
     Evidently HTML report you can open in a browser.

The inference_logs table is created automatically on first startup.
"""
import logging
from os import environ
from typing import Optional

from api.schemas import TransactionInference
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

class InferenceLogger:
    def __init__(self) -> None:
        self.engine = create_engine(
            f"postgresql://{environ['POSTGRES_USER']}:{environ['POSTGRES_PASSWORD']}"
            f"@{environ['POSTGRES_HOST']}:{environ['POSTGRES_PORT']}/{environ['FRAUD_DETECTION_DB']}"
        )
        logger.info("InferenceLogger initialized.")

    def log_inference(
        self,
        transaction_inference: TransactionInference,
        is_fraud: Optional[bool] = None,
    ) -> None:
        with self.engine.connect() as connection:
            connection.execute(
                text(f"""
                    WITH deployed_model AS (
                        INSERT INTO deployed_models (model_name, model_version)
                        VALUES (:model_name, :model_version)
                        ON CONFLICT (model_name, model_version) DO UPDATE SET model_name = EXCLUDED.model_name
                        RETURNING model_id
                    )
                    INSERT INTO transaction_inferences(
                        transaction_id,
                        transaction_timestamp,
                        amount,
                        is_fraud,
                        is_fraud_prediction,
                        is_fraud_probability,
                        model_deployment_id,
                        latency_ms,
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
                        :latency_ms,
                        {",".join([f":v{i}" for i in range(1, 29)])}
                    )
                """),
                {
                    **transaction_inference.model_dump(),
                    "is_fraud": is_fraud if is_fraud is not None else transaction_inference.is_fraud
                }
            )
            connection.commit()

        logger.info(
            f"Logged: pred={transaction_inference.is_fraud_prediction} "
            f"prob={transaction_inference.is_fraud_probability:.4f} "
            f"lat={transaction_inference.latency_ms:.1f}ms"
        )