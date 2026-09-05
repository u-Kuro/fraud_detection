from datetime import datetime, timezone, timedelta

import numpy
from pandas import DataFrame
from pyarrow import parquet

from services.shared.src.modules.configs.mlflow import MLflowConfig
from services.drift_check.src.modules.environment.drift_check import drift_check_environment
from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences
from services.shared.src.repositories.mlflow.mlflow import mlflow_module

def load_reference_dataset() -> tuple[DataFrame, datetime]:
    reference_dataset_parquet = mlflow_module.artifacts.download_artifacts(
        run_id=drift_check_environment.ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID,
        artifact_path=MLflowConfig.reference_dataset_path
    )
    df_reference = parquet.read_table(reference_dataset_parquet).to_pandas()

    if df_reference is None:
        raise ValueError(f"No reference dataset was found in 'runs:/{drift_check_environment.ACTIVE_MODEL_DEPLOYMENT_MLFLOW_RUN_ID}/{MLflowConfig.reference_dataset_path}'.")

    df_reference_max_timestamp = df_reference[TransactionInferences.transaction_timestamp.key].max()
    assert isinstance(df_reference_max_timestamp, numpy.int64)

    dataset_max_timestamp = datetime.fromtimestamp(
        df_reference_max_timestamp,
        timezone.utc
    )
    chosen_current_dataset_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    current_dataset_cutoff = min(chosen_current_dataset_cutoff, dataset_max_timestamp)

    return df_reference, current_dataset_cutoff