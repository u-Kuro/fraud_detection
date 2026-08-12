from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import select, func, or_

from services.shared.modules.configs.dataset import DatasetConfig
from services.shared.modules.configs.postgres import PostgresConfig
from services.shared.modules.schemas.postgres.model_deployments import ModelDeployments
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInferences
from services.train_model.src.modules.schemas.postgres.transaction_inferences import TransactionInferencesDatasetNow
from services.train_model.src.repositories.postgres.postgres import sql_session

def get_timed_latest_unused_dataset() -> TransactionInferencesDatasetNow:
    with sql_session.begin() as session:
        cutoff_subquery = (
            select(func.max(ModelDeployments.dataset_max_timestamp))
            .where(
                ModelDeployments.project_id == PostgresConfig.PROJECT_ID(),
                ModelDeployments.active.is_(True),
            )
            .order_by(ModelDeployments.created_at.desc())
            .limit(1)
            .scalar_subquery()
        )
        df = pd.read_sql(
            select(
                TransactionInferences.is_fraud,
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
                or_(
                    TransactionInferences.transaction_timestamp > cutoff_subquery,
                    cutoff_subquery.is_(None)
                ),
                TransactionInferences.is_fraud.is_not(None),
            )
            .order_by(
                TransactionInferences.transaction_id,
                func.random()
            )
            .limit(DatasetConfig.maximum_dataset_rows),
            session.connection()
        )

        if len(df) < DatasetConfig.minimum_rows:
            raise ValueError(f"Dataset window is too small ({len(df)} rows), minimum is {DatasetConfig.minimum_rows}.")

        # Convert bool to integer
        df[TransactionInferences.is_fraud.key] = df[TransactionInferences.is_fraud.key].astype(int)
        # Convert datetime64[ns, UTC] to seconds
        df_current[TransactionInferences.transaction_timestamp.key] = (
            pd.to_datetime(
                df_current[TransactionInferences.transaction_timestamp.key],
                utc=True
            )
            .astype("datetime64[s, UTC]")
            .astype("int64")
        )

        return TransactionInferencesDatasetNow(
            dataset=df,
            retrieved_iso_datetime=datetime.now(timezone.utc).isoformat()
        )