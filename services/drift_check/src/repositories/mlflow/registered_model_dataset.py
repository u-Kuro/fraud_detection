from datetime import datetime, timezone, timedelta

import mlflow
from pandas import DataFrame
from pyarrow import parquet

from services.drift_check.src.modules.configs.mlflow import MLFlowConfig
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInferences

def load_reference_dataset() -> tuple[DataFrame, datetime]:
    reference_dataset_parquet = mlflow.artifacts.download_artifacts(
        artifact_uri=MLFlowConfig.REFERENCE_DATASET_URI()
    )
    df_reference = parquet.read_table(reference_dataset_parquet).to_pandas()

    if df_reference is None:
        raise RuntimeError(f"No reference dataset was found in {MLFlowConfig.REFERENCE_DATASET_URI()}.")

    df_reference_max_timestamp = df_reference[TransactionInferences.transaction_timestamp.key].max()
    assert isinstance(df_reference_max_timestamp, float)

    dataset_max_timestamp = datetime.fromtimestamp(
        df_reference_max_timestamp,
        timezone.utc
    )
    chosen_current_dataset_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    current_dataset_cutoff = min(chosen_current_dataset_cutoff, dataset_max_timestamp)

    return df_reference, current_dataset_cutoff