from sklearn.preprocessing import RobustScaler
from xgboost import XGBClassifier

from services.shared.controllers.airflow.xcom import xcom_push
from services.shared.modules.configs import MLFlowConfig
from services.shared.modules.schemas import FraudClassificationTransactionTimestamp
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
        timestamp_feature_key=FraudClassificationTransactionTimestamp.model_field_key()
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

# def delete_stale_candidates(
#     client: MlflowClient,
#     model_name: str,
#     current_version: int
# ) -> None:
#     try:
#         versions = client.search_model_versions(f"name='{model_name}'")
#         for item in versions:
#             aliases = getattr(item, "aliases", []) or []
#             version = int(item.version)
#             if version == current_version: continue
#             # Version has candidate alias on it but is not the new one — remove alias and delete
#             if "candidate" in aliases:
#                 try:
#                     client.delete_registered_model_alias(model_name, "candidate")
#                 except: pass
#             # Delete versions that have no aliases and are not in production
#             if "production" not in aliases and "archived" not in aliases:
#                 try:
#                     client.delete_model_version(model_name, str(version))
#                     logger.info(f"Deleted stale candidate model version {model_name} v{version}")
#                 except Exception as e:
#                     logger.warning(f"Could not delete stale version {version}: {e}")
#     except Exception as e:
#         logger.warning(f"Stale candidate cleanup failed (non-fatal): {e}")

# def post_or_update_promotion_slack(
#     promotion_approval_slack_ts: str | None,
#     model_name: str,
#     model_version: int,
#     metrics: dict,
# ) -> str:
#     """Post or update in-place the promotion approval Slack message."""
#     slack = slack_sdk.WebClient(token=slack_environment.SLACK_BOT_USER_AUTH_TOKEN)
#     blocks = [
#         {
#             "type": "header",
#             "text": {
#                 "type": "plain_text",
#                 "text": "✅ Training Complete — Approve for Promotion"
#             }
#         },
#         {
#             "type": "section",
#             "text": {
#                 "type": "mrkdwn",
#                 "text": (
#                     f"Model `{model_name}` v{model_version} is ready.\n"
#                     f"F1: `{metrics['f1']:.4f}` | ROC-AUC: `{metrics['roc_auc']:.4f}`\n\n"
#                     "Approve to promote to production (zero-downtime rolling reload)."
#                 ),
#             },
#         },
#         {
#             "type": "actions",
#             "elements": [
#                 {
#                     "type": "button",
#                     "text": {
#                         "type": "plain_text",
#                         "text": "🚀 Approve Promotion"
#                     },
#                     "style": "primary",
#                     "action_id": "approve_promotion",
#                 },
#                 {
#                     "type": "button",
#                     "text": {
#                         "type": "plain_text",
#                         "text": "❌ Reject"
#                     },
#                     "style": "danger",
#                     "action_id": "reject_promotion",
#                 },
#             ],
#         },
#     ]
#
#     try:
#         if promotion_approval_slack_ts:
#             response = slack.chat_update(
#                 channel=slack_environment.SLACK_CHANNEL_ID,
#                 ts=promotion_approval_slack_ts,
#                 blocks=blocks
#             )
#         else:
#             response = slack.chat_postMessage(
#                 channel=slack_environment.SLACK_CHANNEL_ID,
#                 blocks=blocks
#             )
#         return response["ts"]
#     except Exception as e:
#         logger.warning(f"Slack notification failed (non-fatal): {e}")
#         return promotion_approval_slack_ts or ""