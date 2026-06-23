from datetime import datetime

import pandas as pd
from pandas import DataFrame
from sqlalchemy import text

from services.drift_monitor.src.modules.environment import environment
from services.drift_monitor.src.repositories.postgres import engine


def load_current_window(
    current_cutoff_date: datetime,
) -> DataFrame:
    """Load recent inference data from transaction_inferences."""
    query = text(f"""
        WITH selected AS (
            SELECT DISTINCT ON (transaction_id)
                transaction_timestamp,
                amount,
                {", ".join([f"v{i}" for i in range(1, 29)])},
                is_fraud::INTEGER AS is_fraud,
                is_fraud_prediction::INTEGER AS is_fraud_prediction,
                is_fraud_probability
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
        LIMIT :max_selected_rows
    """)
    with engine.connect() as connection:
        return pd.read_sql(query, connection, params={
            "current_cutoff_date": current_cutoff_date,
            "max_selected_rows": environment.MAX_SELECTED_ROWS
        })