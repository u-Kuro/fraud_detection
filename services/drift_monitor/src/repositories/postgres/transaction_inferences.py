from datetime import datetime

import pandas as pd
from pandas import DataFrame
from sqlalchemy import text

from services.drift_monitor.src.repositories.postgres import engine
from shared.modules.configs.dataset import dataset_config
from shared.modules.schemas import FraudClassificationFeatures, FraudClassificationLabel, FraudClassificationPrediction, FraudClassificationProbability

def load_current_dataset(
    current_dataset_cutoff: datetime,
) -> DataFrame:
    with engine.connect() as connection:
        df_current = pd.read_sql(
            text(f"""
                WITH current_dataset AS (
                    SELECT DISTINCT ON (transaction_id)
                        {",".join(FraudClassificationFeatures.model_field_keys())},
                        {FraudClassificationLabel.model_field_key()}::INTEGER AS {FraudClassificationLabel.model_field_key()},
                        {FraudClassificationPrediction.model_field_key()}::INTEGER AS {FraudClassificationPrediction.model_field_key()},
                        {FraudClassificationProbability.model_field_key()}
                    FROM transaction_inferences
                    WHERE transaction_timestamp > :current_dataset_cutoff
                    ORDER BY 
                        transaction_id DESC,
                        transaction_timestamp DESC,
                        inference_timestamp DESC 
                )
                SELECT * FROM current_dataset
                ORDER BY random()
                LIMIT :MAXIMUM_DATASET_ROWS
           """),
           connection,
           params={
                "current_dataset_cutoff": current_dataset_cutoff,
                "MAXIMUM_DATASET_ROWS": dataset_config.MAXIMUM_DATASET_ROWS
           }
       )

        if len(df_current) < dataset_config.MINIMUM_ROWS:
            raise ValueError(f"Dataset window is too small ({len(df_current)} rows), minimum is {dataset_config.MINIMUM_ROWS}.")

        return df_current