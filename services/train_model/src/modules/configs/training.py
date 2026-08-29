from dataclasses import dataclass

@dataclass(frozen=True)
class TrainingConfig:

    random_state: int = 42
    test_size: float = 0.2
    bayes_steps: int = 30
    training_timeout_seconds: int = 3_600

    @property
    def cv_val_size(self) -> float:
        # 60/20/20 train/val/test — val is 25% of train set (0.2 / 0.8)
        return self.test_size / (1 - self.test_size)