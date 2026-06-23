from pydantic import BaseModel

class Transaction(BaseModel):
    feature_columns: list = ["transaction_timestamp", "amount"] + [f"v{i}" for i in range(1, 29)]
    target_column: str = "is_fraud"