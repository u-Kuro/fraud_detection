from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from services.shared.modules.configs import PostgresConfig
from services.shared.modules.configs.dataset import DatasetConfig
from services.shared.modules.schemas.models_dataset.fraud_classification import FraudClassificationFeaturesKeys
from services.shared.modules.schemas.postgres.model_deployments import ModelDeploymentsColumnKeys
from services.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInferencesColumnKeys
from services.shared.repositories.postgres import engine
from services.train_model.src.modules.schemas.postgres.transaction_inferences import TransactionInferencesDatasetNow

def get_timed_latest_unused_dataset() -> TransactionInferencesDatasetNow:
    with engine.connect() as connection:
        df = pd.read_sql(
            text(f"""
                WITH dataset_cutoff AS ( 
                    SELECT MAX({ModelDeploymentsColumnKeys.dataset_max_timestamp})
                    FROM {PostgresTableKeys.model_deployments}
                    WHERE 
                        {ModelDeploymentsColumnKeys.project_id} = :{ModelDeploymentsColumnKeys.project_id}
                    AND {ModelDeploymentsColumnKeys.active}
                    ORDER BY {ModelDeploymentsColumnKeys.created_at} DESC
                    LIMIT 1
                )
                SELECT {",".join(
                    set(FraudClassificationFeaturesKeys) |
                    { TransactionInferencesColumnKeys.is_fraud }
                )}
                FROM {PostgresTableKeys.transaction_inferences}
                WHERE 
                    {TransactionInferencesColumnKeys.transaction_timestamp} > dataset_cutoff
                AND {TransactionInferencesColumnKeys.is_fraud} IS NOT NULL
                ORDER BY random()
                LIMIT :maximum_dataset_rows
            """),
            connection,
            params={
                ModelDeploymentsColumnKeys.project_id: PostgresConfig.PROJECT_ID(),
                "maximum_dataset_rows": DatasetConfig.maximum_dataset_rows
            }
        )

        if len(df) < DatasetConfig.minimum_rows:
            raise ValueError(f"Dataset window is too small ({len(df)} rows), minimum is {DatasetConfig.minimum_rows}.")

        # Convert datetime64[ns, UTC] to seconds
        df[TransactionInferencesColumnKeys.transaction_timestamp] = df[TransactionInferencesColumnKeys.transaction_timestamp].astype("int64") // 10 ** 9

        return TransactionInferencesDatasetNow(
            dataset=df,
            retrieved_iso_datetime=datetime.now(timezone.utc).isoformat()
        )