from pydantic import BaseModel

class TrainingConfig(BaseModel):
    MAX_SELECTED_ROWS: int = 100_000
    TRAINING_MINIMUM_ROWS: int = 1_000
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    BAYES_STEPS: int = 30
    TRAINING_TIMEOUT_SECONDS: int = 3_600

training_config = TrainingConfig()