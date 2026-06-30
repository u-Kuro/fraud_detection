from datetime import datetime

import pandas as pd
from pandas import DataFrame
from sqlalchemy import text

from services.drift_monitor.src.modules.configs import drift_config
from services.drift_monitor.src.repositories.postgres import engine
from shared.modules.schemas import FraudClassifierFeatures, FraudClassifierLabel, FraudClassificationPrediction, \
    FraudClassificationProbability


def load_current_window(
    current_cutoff_date: datetime,
) -> DataFrame:
    with engine.connect() as connection:
        return pd.read_sql(
            text(f"""
                WITH selected AS (
                    SELECT DISTINCT ON (transaction_id)
                        {",".join(FraudClassifierFeatures.model_field_keys())}
                        {FraudClassifierLabel.model_field_key()}::INTEGER AS {FraudClassifierLabel.model_field_key()},
                        {FraudClassificationPrediction.model_field_key()}::INTEGER AS {FraudClassificationPrediction.model_field_key()},
                        {FraudClassificationProbability.model_field_key()}
                    FROM transaction_inferences
                    WHERE transaction_timestamp > :current_cutoff_date
                    ORDER BY 
                        transaction_id DESC,
                        transaction_timestamp DESC,
                        inference_timestamp DESC 
                )
                SELECT * 
                FROM selected
                ORDER BY random()
                LIMIT :MAXIMUM_CURRENT_DATASET_ROWS
           """),
           connection,
           params={
                "current_cutoff_date": current_cutoff_date,
                "MAXIMUM_CURRENT_DATASET_ROWS": drift_config.MAXIMUM_CURRENT_DATASET_ROWS
           }
       )