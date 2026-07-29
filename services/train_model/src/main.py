from sklearn.preprocessing import RobustScaler
from xgboost import XGBClassifier

from services.shared.controllers.airflow.xcom import xcom_push
from services.shared.modules.configs import MLFlowConfig
from services.shared.modules.schemas.postgres.transaction_inferences import TransactionInferencesColumnKeys
from services.train_model.src.modules.configs import TrainingConfig
from services.train_model.src.modules.configs.airflow.data_keys import TrainingPipelineKeys
from services.train_model.src.modules.configs.hyperparameters import XGBHyperparametersSampler
from services.train_model.src.repositories.mlflow.registered_model import save_and_register_model
from services.train_model.src.repositories.mlflow.run import transactional_mlflow_run, save_model_reference_dataset, save_model_hyperparameters, save_model_metrics
from services.train_model.src.repositories.postgres.transaction_inferences import get_timed_latest_unused_dataset
from services.train_model.src.services.dataset import get_dataset_min_and_max_timestamps
from services.train_model.src.services.evaluation import evaluate_model
from services.train_model.src.services.initialization import seed_everything
from services.train_model.src.services.preprocessing import preprocess
from services.train_model.src.services.training import train_model

def main() -> None:
    seed_everything(TrainingConfig.RANDOM_STATE)

    unused_dataset_outputs = get_timed_latest_unused_dataset()
    preprocess_outputs = preprocess(unused_dataset_outputs.dataset)

    with transactional_mlflow_run(run_name=MLFlowConfig.MODEL_NAME):
        train_model_outputs = train_model(
            preprocess_outputs=preprocess_outputs,
            scaler=RobustScaler,
            model=XGBClassifier,
            hyperparameters_sampler=XGBHyperparametersSampler
        )

        model_evaluations = evaluate_model(
            model=train_model_outputs.model,
            X_test=preprocess_outputs.X_test,
            y_test=preprocess_outputs.y_test
        )

        registered_model_info = save_and_register_model(
            model=train_model_outputs.model,
            X_test_samples=preprocess_outputs.X_test[:5]
        )

        save_model_reference_dataset(
            mlflow_model_run_id=registered_model_info.run_id,
            model_reference_dataset=unused_dataset_outputs.dataset
        )

        save_model_hyperparameters(
            mlflow_model_run_id=registered_model_info.run_id,
            model_hyperparameters=train_model_outputs.hyperparameters
        )

        save_model_metrics(
            mlflow_model_run_id=registered_model_info.run_id,
            mlflow_model_id=registered_model_info.model_id,
            model_metrics=model_evaluations.metrics.model_dump(),
            model_metric_figures=model_evaluations.metric_figures.model_dump()
        )

    dataset_min_max_timestamps = get_dataset_min_and_max_timestamps(
        dataset=unused_dataset_outputs.dataset,
        timestamp_feature_key=TransactionInferencesColumnKeys.transaction_timestamp
    )

    xcom_push({
        TrainingPipelineKeys.MODEL_TRAINED_AT_ISO_DATETIME: unused_dataset_outputs.retrieved_iso_datetime,
        TrainingPipelineKeys.MLFLOW_RUN_ID: registered_model_info.run_id,
        TrainingPipelineKeys.MODEL_NAME: registered_model_info.model_name,
        TrainingPipelineKeys.MODEL_VERSION: registered_model_info.model_version,
        TrainingPipelineKeys.MODEL_DATASET_MIN_ISO_DATETIME: dataset_min_max_timestamps.model_dataset_min_iso_datetime,
        TrainingPipelineKeys.MODEL_DATASET_MAX_ISO_DATETIME: dataset_min_max_timestamps.model_dataset_max_iso_datetime,
        TrainingPipelineKeys.MODEL_F1_SCORE: model_evaluations.metrics.f1_score,
        TrainingPipelineKeys.MODEL_PR_AUC: model_evaluations.metrics.pr_auc,
        TrainingPipelineKeys.MODEL_RECALL: model_evaluations.metrics.recall,
        TrainingPipelineKeys.MODEL_PRECISION: model_evaluations.metrics.precision,
    })

if __name__ == "__main__":
    main()