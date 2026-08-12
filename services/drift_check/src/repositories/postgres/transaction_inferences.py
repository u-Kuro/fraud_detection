from datetime import datetime

import pandas as pd
from pandas import DataFrame
from sqlalchemy import select, func

from services.drift_check.src.repositories.postgres.postgres import sql_session
from services.shared.modules.configs.dataset import DatasetConfig
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInferences

def load_current_dataset(
    current_dataset_cutoff: datetime,
) -> DataFrame:
    with sql_session.begin() as session:
        current_dataset_subquery = (
            select(
                TransactionInferences.is_fraud,
                TransactionInferences.is_fraud_prediction,
                TransactionInferences.is_fraud_probability,
                TransactionInferences.amount,
                TransactionInferences.transaction_timestamp,
                TransactionInferences.v1, TransactionInferences.v2,
                TransactionInferences.v3, TransactionInferences.v4,
                TransactionInferences.v5, TransactionInferences.v6,
                TransactionInferences.v7, TransactionInferences.v8,
                TransactionInferences.v9, TransactionInferences.v10,
                TransactionInferences.v11, TransactionInferences.v12,
                TransactionInferences.v13, TransactionInferences.v14,
                TransactionInferences.v15, TransactionInferences.v16,
                TransactionInferences.v17, TransactionInferences.v18,
                TransactionInferences.v19, TransactionInferences.v20,
                TransactionInferences.v21, TransactionInferences.v22,
                TransactionInferences.v23, TransactionInferences.v24,
                TransactionInferences.v25, TransactionInferences.v26,
                TransactionInferences.v27, TransactionInferences.v28,
            )
            .distinct(TransactionInferences.transaction_id)
            .where(
                TransactionInferences.transaction_timestamp > current_dataset_cutoff,
                TransactionInferences.is_fraud_prediction.is_not(None),
                TransactionInferences.is_fraud_probability.is_not(None)
            )
            .order_by(
                TransactionInferences.transaction_id,
                TransactionInferences.created_at.desc()
            )
            .subquery()
        )
        df_current = pd.read_sql(
            select(current_dataset_subquery)
            .order_by(func.random())
            .limit(DatasetConfig.maximum_dataset_rows),
            session.connection(),
       )

        if len(df_current) < DatasetConfig.minimum_rows:
            raise ValueError(f"Dataset window is too small ({len(df_current)} rows), minimum is {DatasetConfig.minimum_rows}.")

        # Convert bool to float64 (int64 is non-nullable)
        df_current[TransactionInferences.is_fraud.key] = df_current[TransactionInferences.is_fraud.key].astype("float64")
        # Convert bool to int64
        df_current[TransactionInferences.is_fraud_prediction.key] = df_current[TransactionInferences.is_fraud_prediction.key].astype("int64")
        # Convert datetime64[ns, UTC] to seconds (int64)
        df_current[TransactionInferences.transaction_timestamp.key] = (
            pd.to_datetime(
                df_current[TransactionInferences.transaction_timestamp.key],
                utc=True
            )
            .astype("datetime64[s, UTC]")
            .astype("int64")
        )

        return df_current