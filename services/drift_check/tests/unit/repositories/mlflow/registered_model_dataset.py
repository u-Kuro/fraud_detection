from datetime import datetime

import pandas
import pyarrow
from pandas import DataFrame
from pytest_mock import MockerFixture

from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

def test_load_reference_dataset(mocker: MockerFixture):
    table = pyarrow.table({
        TransactionInferences.transaction_timestamp.key: [1]
    })
    mocker.patch(
        "services.drift_check.src.repositories.mlflow.registered_model_dataset.parquet.read_table",
        return_value=table
    )

    from services.drift_check.src.repositories.mlflow.registered_model_dataset import load_reference_dataset
    df_reference, current_dataset_cutoff = load_reference_dataset()

    assert isinstance(df_reference, DataFrame)
    assert isinstance(current_dataset_cutoff, datetime)
    pandas.testing.assert_frame_equal(df_reference, table.to_pandas())