from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import select, func

from services.shared.modules.configs.dataset import DatasetConfig
from services.shared.modules.configs.postgres import PostgresConfig
from services.shared.modules.schemas.postgres.model_deployments import ModelDeployment
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInference
from services.train_model.src.modules.schemas.postgres.transaction_inferences import TransactionInferencesDatasetNow
from services.train_model.src.repositories.postgres.postgres import sql_session

def get_timed_latest_unused_dataset() -> TransactionInferencesDatasetNow:
    with sql_session.begin() as session:
        cutoff_subquery = (
            select(func.max(ModelDeployment.dataset_max_timestamp))
            .where(
                ModelDeployment.project_id == PostgresConfig.PROJECT_ID(),
                ModelDeployment.active.is_(True),
            )
            .order_by(ModelDeployment.created_at.desc())
            .limit(1)
            .scalar_subquery()
        )
        df = pd.read_sql(
            select(
                TransactionInference.is_fraud,
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
            .where(
                TransactionInference.transaction_timestamp > cutoff_subquery,
                TransactionInference.is_fraud.is_not(None),
            )
            .order_by(func.random())
            .limit(DatasetConfig.maximum_dataset_rows),
            session.connection()
        )

        if len(df) < DatasetConfig.minimum_rows:
            raise ValueError(f"Dataset window is too small ({len(df)} rows), minimum is {DatasetConfig.minimum_rows}.")

        # Convert datetime64[ns, UTC] to seconds
        df[TransactionInference.transaction_timestamp.key] = df[TransactionInference.transaction_timestamp.key].astype("int64") // 10 ** 9

        return TransactionInferencesDatasetNow(
            dataset=df,
            retrieved_iso_datetime=datetime.now(timezone.utc).isoformat()
        )