from pydantic import BaseModel

from shared.schemas import Transaction

class TrainingConfig(BaseModel, Transaction):
    """Fixed training constants. Not environment-driven."""
    max_selected_rows: int = 100_000
    training_minimum_rows: int = 1_000
    random_state: int = 42
    test_size: float = 0.2
    bayes_steps: int = 30
    training_timeout_seconds: int = 3_600

    @property
    def POSTGRES_FRAUD_DB_URL(self) -> str:
        return "postgresql+psycopg2://"

    @property
    def S3_PIPELINE_REFERENCE_PATH(self) -> str:
        return "pipeline/reference"

    @property
    def S3_PIPELINE_DATASETS_PATH(self) -> str:
        return "pipeline/datasets"

training_config = TrainingConfig()
