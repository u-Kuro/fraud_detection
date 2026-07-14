from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from services.shared.modules.configs import postgres_config
from services.shared.modules.configs.dataset import dataset_config
from services.shared.modules.schemas import FraudClassificationDataset, FraudClassificationLabel
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
                "project_id": postgres_config.PROJECT_ID,
                "MAXIMUM_DATASET_ROWS": dataset_config.MAXIMUM_DATASET_ROWS
            }
        )

        if len(df) < dataset_config.MINIMUM_ROWS:
            raise ValueError(f"Dataset window is too small ({len(df)} rows), minimum is {dataset_config.MINIMUM_ROWS}.")

        return TransactionInferencesDatasetNow(
            dataset=df,
            retrieved_iso_datetime=datetime.now(timezone.utc).isoformat()
        )