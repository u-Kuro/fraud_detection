from pydantic import BaseModel, ConfigDict, computed_field

class TrainingConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    BAYES_STEPS: int = 30
    TRAINING_TIMEOUT_SECONDS: int = 3_600

    @computed_field
    @property
    def CV_VAL_SIZE(self) -> float:
        # 60/20/20 train/val/test — val is 25% of train set (0.2 / 0.8)
        return self.TEST_SIZE / (1 - self.TEST_SIZE)

training_config = TrainingConfig()