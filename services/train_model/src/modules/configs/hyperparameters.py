from dataclasses import dataclass, fields
from typing import Callable

from optuna import Trial

@dataclass(frozen=True)
class XGBHyperparametersSampler:
    type HyperparamSampler = Callable[[Trial], int | float]

    n_estimators: HyperparamSampler = lambda trial: trial.suggest_int("n_estimators", 100, 500)
    max_depth: HyperparamSampler = lambda trial: trial.suggest_int("max_depth", 3, 10)
    learning_rate: HyperparamSampler = lambda trial: trial.suggest_float("learning_rate", 0.005, 0.3, log=True)
    subsample: HyperparamSampler = lambda trial: trial.suggest_float("subsample", 0.5, 1.0)
    colsample_bytree: HyperparamSampler = lambda trial: trial.suggest_float("colsample_bytree", 0.4, 1.0)
    reg_alpha: HyperparamSampler = lambda trial: trial.suggest_float("reg_alpha", 1e-6, 1.0, log=True)
    reg_lambda: HyperparamSampler = lambda trial: trial.suggest_float("reg_lambda", 1e-6, 5.0, log=True)
    gamma: HyperparamSampler = lambda trial: trial.suggest_float("gamma", 0.0, 5.0)
    min_child_weight: HyperparamSampler = lambda trial: trial.suggest_int("min_child_weight", 1, 10)

    def resolve(self, trial: Trial) -> dict[str, int | float]:
        return {
            f.name: getattr(self, f.name)(trial)
            for f in fields(self)
        }