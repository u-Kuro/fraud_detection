import pandas as pd
from pandas import DataFrame
from sqlalchemy import text

from services.training_pipeline.src.repositories.postgres import engine
from services.shared.modules.configs import postgres_config
from services.shared.modules.configs.dataset import dataset_config
from services.shared.modules.schemas import FraudClassificationDataset, FraudClassificationLabel, FraudClassificationTransactionTimestamp

def get_latest_unused_dataset() -> DataFrame:
    with engine.connect() as connection:
        df = pd.read_sql(
            text(f"""
                WITH dataset_cutoff AS ( 
                    SELECT MAX(dataset_max_date)
                    FROM model_deployments
                    WHERE 
                        project_id = :project_id
                    AND active
                    ORDER BY created_at DESC
                    LIMIT 1
                )
                SELECT {",".join(FraudClassificationDataset.model_field_keys())}
                FROM transaction_inferences
                WHERE 
                    inference_timestamp > dataset_cutoff
                AND {FraudClassificationLabel.model_field_key()} IS NOT NULL
                ORDER BY random()
                LIMIT :MAXIMUM_DATASET_ROWS
            """),
            connection,
            params={
                "project_id": postgres_config.PROJECT_ID,
                "MAXIMUM_DATASET_ROWS": dataset_config.MAXIMUM_DATASET_ROWS
            }
        )
        transaction_timestamp_key = FraudClassificationTransactionTimestamp.model_field_key()
        df[transaction_timestamp_key] = df[transaction_timestamp_key].apply(lambda x: int(x.timestamp()))
        return df