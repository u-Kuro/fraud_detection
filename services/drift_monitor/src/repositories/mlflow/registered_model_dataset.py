from datetime import datetime, timezone, timedelta

import mlflow
from pandas import DataFrame
from pyarrow import parquet

from shared.modules.configs import mlflow_config
from shared.modules.schemas import FraudClassificationTransactionTimestamp

def load_reference_dataset() -> tuple[DataFrame, datetime]:
    reference_dataset_parquet = mlflow.artifacts.download_artifacts(
        artifact_uri=mlflow_config.REFERENCE_DATASET_URI
    )
    df_reference = parquet.read_table(reference_dataset_parquet).to_pandas()

    if df_reference is None:
        raise RuntimeError(f"No reference dataset was found in {mlflow_config.REFERENCE_DATASET_URI}.")

    dataset_max_timestamp = datetime.fromtimestamp(
        df_reference[FraudClassificationTransactionTimestamp.model_field_key()].max(),
        timezone.utc
    )
    chosen_current_dataset_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    current_dataset_cutoff = min(chosen_current_dataset_cutoff, dataset_max_timestamp)

    return df_reference, current_dataset_cutoff