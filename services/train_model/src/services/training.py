import numpy as np
import optuna
from optuna import Study
from optuna.samplers import TPESampler
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
from xgboost import XGBClassifier

from services.shared.modules.configs import mlflow_config
from services.train_model.src.modules.configs import training_config
from services.train_model.src.modules.configs.hyperparameters import XGBHyperparametersSampler
from services.train_model.src.modules.schemas.preprocessing import PreprocessOutputs
from services.train_model.src.modules.schemas.training import TrainModelOutputs

def train_model(
    preprocess_outputs: PreprocessOutputs,
    scaler: type[RobustScaler],
    model: type[XGBClassifier],
    hyperparameters_sampler: type[XGBHyperparametersSampler],
) -> TrainModelOutputs:
    model_results = optimize_model_hyperparameters(
        preprocessed_output=preprocess_outputs,
        scaler=scaler,
        model=model,
        hyperparameters_sampler=hyperparameters_sampler()
    )

    best_model_hyperparameters = model_results.best_params
    best_model = Pipeline(
        [
            (mlflow_config.SCALER_NAME, scaler()),
            (
                mlflow_config.MODEL_NAME,
                model(
                    **best_model_hyperparameters,
                    scale_pos_weight=preprocess_outputs.original_y_train_positive_scale,
                    random_state=training_config.RANDOM_STATE,
                    n_jobs=-1,
                    verbosity=2,
                ),
            ),
        ]
    ).fit(
        preprocess_outputs.X_train,
        preprocess_outputs.y_train
    )

    return TrainModelOutputs(
        model=best_model,
        hyperparameters=best_model_hyperparameters
    )

def optimize_model_hyperparameters(
    preprocessed_output: PreprocessOutputs,
    scaler: type[RobustScaler],
    model: type[XGBClassifier],
    hyperparameters_sampler: XGBHyperparametersSampler,
) -> Study:
    def objective(trial: optuna.Trial) -> float:
        estimator = Pipeline([
            (mlflow_config.SCALER_NAME, scaler()),
            (
                mlflow_config.MODEL_NAME,
                model(
                    **hyperparameters_sampler.resolve(trial),
                    scale_pos_weight=preprocessed_output.original_y_train_positive_scale,
                    random_state=training_config.RANDOM_STATE,
                    n_jobs=-1,
                    verbosity=2,
                ),
            ),
        ])

        model_score = float(
            np.mean(
                cross_val_score(
                    estimator,
                    preprocessed_output.X_train,
                    preprocessed_output.y_train,
                    cv=preprocessed_output.cross_validation,
                    scoring="average_precision",
                    n_jobs=1,
                )
            )
        )

        return model_score

    study = optuna.create_study(
        direction="maximize",
        sampler=TPESampler(
            seed=training_config.RANDOM_STATE,
            multivariate=True
        ),
    )
    study.optimize(
        objective,
        n_trials=training_config.BAYES_STEPS,
        n_jobs=1,
        show_progress_bar=True,
        gc_after_trial=True,
        timeout=training_config.TRAINING_TIMEOUT_SECONDS,
    )

    return study