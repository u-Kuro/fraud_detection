from datetime import datetime

import pandas as pd
from pandas import DataFrame
from sqlalchemy import text

from services.drift_check.src.repositories.postgres import engine
from services.shared.modules.configs.dataset import DatasetConfig
from services.shared.modules.schemas.postgres.postgres import PostgresTableKeys
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInferencesColumnKeys

def load_current_dataset(
    current_dataset_cutoff: datetime,
) -> DataFrame:
    with engine.connect() as connection:
        df_current = pd.read_sql(
            text(f"""
                WITH current_dataset AS (
                    SELECT DISTINCT ON ({TransactionInferencesColumnKeys.transaction_id})
                    {",".join(
                        set(TransactionInferencesColumnKeys) |
                        {f"{TransactionInferencesColumnKeys.is_fraud}::INTEGER AS {TransactionInferencesColumnKeys.is_fraud}"} |
                        {f"{TransactionInferencesColumnKeys.is_fraud_prediction}::INTEGER AS {TransactionInferencesColumnKeys.is_fraud_prediction}"} |
                        {TransactionInferencesColumnKeys.is_fraud_probability}
                    )}
                    FROM {PostgresTableKeys.transaction_inferences}
                    WHERE {TransactionInferencesColumnKeys.transaction_timestamp} > :current_dataset_cutoff
                    ORDER BY 
                        {TransactionInferencesColumnKeys.transaction_id} DESC,
                        {TransactionInferencesColumnKeys.transaction_timestamp} DESC,
                        {TransactionInferencesColumnKeys.created_at} DESC 
                )
                SELECT * FROM current_dataset
                ORDER BY random()
                LIMIT :maximum_dataset_rows
           """),
           connection,
           params={
                "current_dataset_cutoff": current_dataset_cutoff,
                "maximum_dataset_rows": DatasetConfig.maximum_dataset_rows
           }
       )

        if len(df_current) < DatasetConfig.minimum_rows:
            raise ValueError(f"Dataset window is too small ({len(df_current)} rows), minimum is {DatasetConfig.minimum_rows}.")

        return df_current