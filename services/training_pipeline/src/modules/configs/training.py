from pydantic import BaseModel, ConfigDict

class TrainingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    MAXIMUM_TRAINING_DATASET_ROWS: int = 100_000
    MINIMUM_TRAINING_DATASET_ROWS: int = 1_000
    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    BAYES_STEPS: int = 30
    TRAINING_TIMEOUT_SECONDS: int = 3_600

training_config = TrainingConfig()