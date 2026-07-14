from pandas import DataFrame
from pydantic import BaseModel, ConfigDict

class TransactionInferencesDatasetNow(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset: DataFrame
    retrieved_iso_datetime: str