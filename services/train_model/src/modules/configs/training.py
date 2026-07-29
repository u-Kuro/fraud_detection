from dataclasses import dataclass

@dataclass(frozen=True)
class TrainingConfig:

    RANDOM_STATE: int = 42
    TEST_SIZE: float = 0.2
    BAYES_STEPS: int = 30
    TRAINING_TIMEOUT_SECONDS: int = 3_600

    @classmethod
    def CV_VAL_SIZE(cls) -> float:
        # 60/20/20 train/val/test — val is 25% of train set (0.2 / 0.8)
        return cls.TEST_SIZE / (1 - cls.TEST_SIZE)