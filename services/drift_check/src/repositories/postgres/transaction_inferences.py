from datetime import datetime

import pandas as pd
from pandas import DataFrame
from sqlalchemy import select, func

from services.drift_check.src.repositories.postgres.postgres import sql_session
from services.shared.modules.configs.dataset import DatasetConfig
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInference

def load_current_dataset(
    current_dataset_cutoff: datetime,
) -> DataFrame:
    with sql_session.begin() as session:
        current_dataset_subquery = (
            select(
                TransactionInference.is_fraud,
                TransactionInference.is_fraud_prediction,
                TransactionInference.is_fraud_probability,
                TransactionInference.amount,
                TransactionInference.transaction_timestamp,
                TransactionInference.v1, TransactionInference.v2,
                TransactionInference.v3, TransactionInference.v4,
                TransactionInference.v5, TransactionInference.v6,
                TransactionInference.v7, TransactionInference.v8,
                TransactionInference.v9, TransactionInference.v10,
                TransactionInference.v11, TransactionInference.v12,
                TransactionInference.v13, TransactionInference.v14,
                TransactionInference.v15, TransactionInference.v16,
                TransactionInference.v17, TransactionInference.v18,
                TransactionInference.v19, TransactionInference.v20,
                TransactionInference.v21, TransactionInference.v22,
                TransactionInference.v23, TransactionInference.v24,
                TransactionInference.v25, TransactionInference.v26,
                TransactionInference.v27, TransactionInference.v28,
            )
            .distinct(TransactionInference.transaction_id)
            .where(
                TransactionInference.transaction_timestamp > current_dataset_cutoff
            )
            .order_by(
                TransactionInference.transaction_id.desc(),
                TransactionInference.transaction_timestamp.desc(),
                TransactionInference.created_at.desc(),
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

        df_current[TransactionInference.is_fraud.key] = df_current[TransactionInference.is_fraud.key].astype(int)
        df_current[TransactionInference.is_fraud_prediction.key] = df_current[TransactionInference.is_fraud_prediction.key].astype(int)
        df_current[TransactionInference.transaction_timestamp.key] = (
            pd.to_datetime(
                df_current[TransactionInference.transaction_timestamp.key],
                utc=True
            )
            .astype("int64") // 10 ** 9
        )

        return df_current