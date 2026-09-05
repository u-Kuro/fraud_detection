from datetime import datetime

import pandas
from pandas import DataFrame
from pytest_mock import MockerFixture

from services.shared.src.modules.configs.dataset import DatasetConfig
from services.shared.src.modules.schemas.postgres.transaction_inferences import TransactionInferences

def test_load_current_dataset(mocker: MockerFixture):
    dataframe = DataFrame({
        TransactionInferences.is_fraud.key: [1.0],
        TransactionInferences.is_fraud_prediction.key: [1],
        TransactionInferences.is_fraud_probability.key: [1.0],
        TransactionInferences.amount.key: [1.0],
        TransactionInferences.transaction_timestamp.key: [datetime.now()],
    })
    mocker.patch.object(dataframe, "__len__", return_value=DatasetConfig.minimum_rows)
    mocker.patch(
        "services.drift_check.src.repositories.postgres.transaction_inferences.pandas.read_sql",
        return_value=dataframe
    )

    from services.drift_check.src.repositories.postgres.transaction_inferences import load_current_dataset
    result = load_current_dataset(current_dataset_cutoff=datetime.now())

    assert isinstance(result, DataFrame)
    pandas.testing.assert_frame_equal(dataframe, result)
