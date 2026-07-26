from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from services.shared.modules.configs import PostgresConfig
from services.shared.modules.configs.dataset import DatasetConfig
from services.shared.modules.schemas import FraudClassificationDataset, FraudClassificationLabel, \
    FraudClassificationTransactionTimestamp
from services.shared.repositories.postgres import engine
from services.train_model.src.modules.schemas.postgres.transaction_inferences import TransactionInferencesDatasetNow

def get_timed_latest_unused_dataset() -> TransactionInferencesDatasetNow:
    with engine.connect() as connection:
        df = pd.read_sql(
            text(f"""
                WITH dataset_cutoff AS ( 
                    SELECT MAX(dataset_max_date)
                    FROM model_deployments
                    WHERE 
                        project_id = :project_id
                    AND active
                    ORDER BY created_at DESC
                    LIMIT 1
                )
                SELECT {",".join(FraudClassificationDataset.model_field_keys())}
                FROM transaction_inferences
                WHERE 
                    inference_timestamp > dataset_cutoff
                AND {FraudClassificationLabel.model_field_key()} IS NOT NULL
                ORDER BY random()
                LIMIT :MAXIMUM_DATASET_ROWS
            """),
            connection,
            params={
                "project_id": PostgresConfig.PROJECT_ID(),
                "MAXIMUM_DATASET_ROWS": DatasetConfig.MAXIMUM_DATASET_ROWS
            }
        )

        if len(df) < DatasetConfig.MINIMUM_ROWS:
            raise ValueError(f"Dataset window is too small ({len(df)} rows), minimum is {DatasetConfig.MINIMUM_ROWS}.")

        # Convert datetime64[ns, UTC] to seconds
        df[FraudClassificationTransactionTimestamp.model_field_key()] = df[FraudClassificationTransactionTimestamp.model_field_key()].astype("int64") // 10 ** 9

        return TransactionInferencesDatasetNow(
            dataset=df,
            retrieved_iso_datetime=datetime.now(timezone.utc).isoformat()
        )