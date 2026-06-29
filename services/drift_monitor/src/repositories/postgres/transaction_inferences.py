from datetime import datetime

import pandas as pd
from pandas import DataFrame
from sqlalchemy import text

from services.drift_monitor.src.modules.configs import drift_config
from services.drift_monitor.src.repositories.postgres import engine
from shared.modules.configs import fraud_classifier_config

def load_current_window(
    current_cutoff_date: datetime,
) -> DataFrame:
    with engine.connect() as connection:
        return pd.read_sql(
            text(f"""
                WITH selected AS (
                    SELECT DISTINCT ON (transaction_id)
                        transaction_timestamp,
                        amount,
                        {",".join(fraud_classifier_config.FRAUD_CLASSIFIER_FEATURES)}
                        {fraud_classifier_config.FRAUD_CLASSIFIER_LABEL}::INTEGER AS {fraud_classifier_config.FRAUD_CLASSIFIER_LABEL},
                        {fraud_classifier_config.FRAUD_CLASSIFIER_PREDICTION_LABEL}::INTEGER AS {fraud_classifier_config.FRAUD_CLASSIFIER_PREDICTION_LABEL},
                        {fraud_classifier_config.FRAUD_CLASSIFIER_PROBABILITY_LABEL}
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