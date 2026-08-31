from typing import Annotated

from pandas import DataFrame
from pydantic import BaseModel, ConfigDict, StrictStr, Strict

class TransactionInferencesDatasetNow(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dataset: Annotated[DataFrame, Strict()]
    retrieved_iso_datetime: StrictStr