import json, os, sys, tempfile
import random
import shutil
from uuid import UUID

import mlflow
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import optuna
import slack_sdk
from imblearn.over_sampling import SMOTE
from matplotlib import pyplot as plt, ticker
from mlflow import MlflowClient
from mlflow.models import infer_signature
from optuna.samplers import TPESampler
from sklearn.metrics import f1_score, roc_auc_score, ConfusionMatrixDisplay, accuracy_score, precision_score, \
    recall_score, average_precision_score
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
from xgboost import XGBClassifier

from services.training_pipeline.src.controllers.slack import update_promotion_approval
from services.training_pipeline.src.modules.configs import training_config
from services.training_pipeline.src.modules.environments.dags import dags_environment
from services.training_pipeline.src.repositories.postgres.model_deployment_workflows import (
    get_deployment_workflow,
    get_latest_unused_dataset,
    update_deployment_workflow,
    update_promotion_approval_slack_ts,
)
from services.training_pipeline.src.services.promote import promote
from shared.modules.configs import mlflow_config
from shared.modules.configs.dataset import dataset_config
from shared.modules.environment import slack_environment
from shared.modules.logging import logger
from shared.modules.schemas import FraudClassificationLabel, FraudClassificationTransactionTimestamp

def get_predictions_sklearn(
    model: object,
    x: np.ndarray,
    threshold: float = 0.5
) -> dict[str, np.ndarray]:
    y_prob = model.predict_proba(x)[:, 1]
    return {
        "y_pred": (y_prob >= threshold).astype(int),
        "y_prob": y_prob
    }


def evaluate_model_predictions(
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    y_true: np.ndarray
) -> dict:
    return {
        "F1 score": f1_score(y_true, y_pred),
        "PR-AUC": average_precision_score(y_true, y_prob),
        "Recall": recall_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred),
        "ROC-AUC": roc_auc_score(y_true, y_prob),
        "Accuracy": accuracy_score(y_true, y_pred),
    }


def visualize_model_predictions(
    title: str,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    y_true: np.ndarray,
    threshold: float = 0.5,
) -> dict:
    confusion_matrix_figure, confusion_matrix_ax = plt.subplots()
    ConfusionMatrixDisplay.from_predictions(
        y_true,
        y_pred,
        display_labels=["Legitimate", "Fraud"],
        normalize="true",
        cmap="Blues",
        values_format=".1%",
        ax=confusion_matrix_ax,
    )
    confusion_matrix_ax.set_title(title)

    probability_scatter_figure, probability_scatter_ax = plt.subplots()
    probability_scatter_ax.scatter(
        y_prob,
        range(len(y_true)),
        c=np.where(y_true == 1, "red", "blue"),
        edgecolors="k",
    )
    probability_scatter_ax.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
    probability_scatter_ax.axvline(x=threshold, alpha=0.3, color="white", linestyle="--")
    probability_scatter_ax.axvspan(threshold, 1.0, alpha=0.05, color="red")
    probability_scatter_ax.axvspan(0.0, threshold, alpha=0.05, color="blue")
    probability_scatter_ax.set_yticks([])
    probability_scatter_ax.set_ylabel("Transactions")
    probability_scatter_ax.set_xlabel("Fraud Probability Score")
    probability_scatter_ax.set_title(title)

    return {
        f"probability_scatter_{title.lower()}": probability_scatter_figure,
        f"confusion_matrix_{title.lower()}": confusion_matrix_figure,
    }

def train_model(model_deployment_workflow_id: UUID) -> tuple[str, int, dict]:
    df = get_latest_unused_dataset()

    mlflow.set_tracking_uri(mlflow_config.TRACKING_URI)
    mlflow.set_experiment(mlflow_config.EXPERIMENT_NAME)

    random.seed(training_config.RANDOM_STATE)
    np.random.seed(training_config.RANDOM_STATE)

    label_key = FraudClassificationLabel.model_field_key()
    x = df.drop(label_key, axis=1).values
    y = df[label_key].values

    train_x, test_x, train_y, test_y = train_test_split(
        x, y,
        test_size=training_config.TEST_SIZE,
        random_state=training_config.RANDOM_STATE,
        stratify=y
    )

    positive_weight = (train_y == 0).sum() / (train_y == 1).sum()

    smote = SMOTE(random_state=training_config.RANDOM_STATE)
    train_x, train_y = smote.fit_resample(train_x, train_y)

    cv = StratifiedKFold(
        n_splits=int(1 / training_config.CV_VAL_SIZE),
        shuffle=True,
        random_state=training_config.RANDOM_STATE
    )
    with mlflow.start_run(run_name=mlflow_config.MODEL_NAME) as run:
        try:
            def objective(trial: optuna.Trial) -> float:
                model_parameters = {
                    "n_estimators":     trial.suggest_int("n_estimators", 100, 500),
                    "max_depth":        trial.suggest_int("max_depth", 3, 10),
                    "learning_rate":    trial.suggest_float("learning_rate", 0.005, 0.3, log=True),
                    "subsample":        trial.suggest_float("subsample", 0.5, 1.0),
                    "colsample_bytree": trial.suggest_float("colsample_bytree", 0.4, 1.0),
                    "reg_alpha":        trial.suggest_float("reg_alpha", 1e-6, 1.0, log=True),
                    "reg_lambda":       trial.suggest_float("reg_lambda", 1e-6, 5.0, log=True),
                    "gamma":            trial.suggest_float("gamma", 0.0, 5.0),
                    "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
                }

                return float(
                    np.mean(
                        cross_val_score(
                            Pipeline([
                                (mlflow_config.SCALER_NAME, RobustScaler()),
                                (
                                    mlflow_config.MODEL_NAME,
                                    XGBClassifier(
                                        **model_parameters,
                                        scale_pos_weight=positive_weight,
                                        random_state=training_config.RANDOM_STATE,
                                        n_jobs=-1,
                                        verbosity=2,
                                    ),
                                ),
                            ]),
                            train_x,
                            train_y,
                            cv=cv,
                            scoring="average_precision",
                            n_jobs=1,
                        )
                    )
                )

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

            best_model_parameters = study.best_params
            best_model = Pipeline(
                [
                    (mlflow_config.SCALER_NAME, RobustScaler()),
                    (
                        mlflow_config.MODEL_NAME,
                        XGBClassifier(
                            **best_model_parameters,
                            scale_pos_weight=positive_weight,
                            random_state=training_config.RANDOM_STATE,
                            n_jobs=-1,
                            verbosity=2,
                        ),
                    ),
                ]
            ).fit(train_x, train_y)

            model_predictions = get_predictions_sklearn(best_model, test_x)
            model_metrics = evaluate_model_predictions(
                **model_predictions,
                y_true=test_y
            )
            model_metric_figures = visualize_model_predictions(
                **model_predictions,
                y_true=test_y,
                title=mlflow_config.MODEL_NAME
            )

            model_info = mlflow.sklearn.log_model(
                sk_model=best_model,
                serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_SKOPS,
                registered_model_name=mlflow_config.MODEL_NAME,
                signature=infer_signature(
                    model_input=test_x,
                    model_output=best_model.predict(test_x)
                ),
                input_example=test_x[:5],
                pip_requirements=[
                    "xgboost==3.2.0",
                    "scikit-learn==1.8.0",
                    "numpy==2.4.6",
                    "pandas==2.3.3",
                ],
                name=mlflow_config.MODEL_PATH,
                skops_trusted_types=[
                    "xgboost.core.Booster",
                    "xgboost.sklearn.XGBClassifier",
                ],
            )
            if model_info.registered_model_version is None:
                raise RuntimeError("Model registration failed: registered_model_version is None.")

            temporary_directory = tempfile.mkdtemp()
            try:
                dataset_reference_file_path = os.path.join(temporary_directory, "reference.parquet")
                pq.write_table(
                    table=pa.table(df),
                    where=dataset_reference_file_path
                )
                mlflow.log_artifact(
                    local_path=dataset_reference_file_path,
                    artifact_path=mlflow_config.REFERENCE_DATASET_PATH,
                    run_id=model_info.run_id
                )
            finally: shutil.rmtree(temporary_directory)

            mlflow.log_params(
                params=best_model_parameters,
                synchronous=True,
                run_id=model_info.run_id
            )

            mlflow.log_metrics(
                metrics=model_metrics,
                synchronous=True,
                run_id=model_info.run_id,
                model_id=model_info.model_id,
            )

            for name, figure in model_metric_figures.items():
                mlflow.log_figure(
                    figure=figure,
                    artifact_file=f"{name}.png"
                )
        except:
            run_id_str = str(run.info.run_id)
            mlflow_client = MlflowClient()
            mlflow.delete_run(run_id_str)
            try:
                versions = mlflow_client.search_model_versions(f"run_id='{run_id_str}'")
                for v in versions:
                    mlflow_client.delete_model_version(name=v.name, version=v.version)
            except: pass
            raise RuntimeError("Model registration failed.")

        transaction_timestamps = df[FraudClassificationTransactionTimestamp.model_field_key()]
        model_dataset_min_timestamp = int(transaction_timestamps.min())
        model_dataset_max_timestamp = int(transaction_timestamps.max())

        update_deployment_workflow(
            model_deployment_workflow_id,
            mlflow_config.MODEL_NAME,
            model_info.registered_model_version,
            model_dataset_min_timestamp,
            model_dataset_max_timestamp
        )

        return mlflow_config.MODEL_NAME, model_info.registered_model_version, model_metrics

def delete_stale_candidates(
    client: MlflowClient,
    model_name: str,
    current_version: int
) -> None:
    try:
        versions = client.search_model_versions(f"name='{model_name}'")
        for item in versions:
            aliases = getattr(item, "aliases", []) or []
            version = int(item.version)
            if version == current_version: continue
            # Version has candidate alias on it but is not the new one — remove alias and delete
            if "candidate" in aliases:
                try:
                    client.delete_registered_model_alias(model_name, "candidate")
                except: pass
            # Delete versions that have no aliases and are not in production
            if "production" not in aliases and "archived" not in aliases:
                try:
                    client.delete_model_version(model_name, str(version))
                    logger.info(f"Deleted stale candidate model version {model_name} v{version}")
                except Exception as e:
                    logger.warning(f"Could not delete stale version {version}: {e}")
    except Exception as e:
        logger.warning(f"Stale candidate cleanup failed (non-fatal): {e}")

def post_or_update_promotion_slack(
    promotion_approval_slack_ts: str | None,
    model_name: str,
    model_version: int,
    metrics: dict,
) -> str:
    """Post or update in-place the promotion approval Slack message."""
    slack = slack_sdk.WebClient(token=slack_environment.SLACK_BOT_USER_AUTH_TOKEN)
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "✅ Training Complete — Approve for Promotion"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"Model `{model_name}` v{model_version} is ready.\n"
                    f"F1: `{metrics['f1']:.4f}` | ROC-AUC: `{metrics['roc_auc']:.4f}`\n\n"
                    "Approve to promote to production (zero-downtime rolling reload)."
                ),
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🚀 Approve Promotion"
                    },
                    "style": "primary",
                    "action_id": "approve_promotion",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "❌ Reject"
                    },
                    "style": "danger",
                    "action_id": "reject_promotion",
                },
            ],
        },
    ]

    try:
        if promotion_approval_slack_ts:
            response = slack.chat_update(
                channel=slack_environment.SLACK_CHANNEL_ID,
                ts=promotion_approval_slack_ts,
                blocks=blocks
            )
        else:
            response = slack.chat_postMessage(
                channel=slack_environment.SLACK_CHANNEL_ID,
                blocks=blocks
            )
        return response["ts"]
    except Exception as e:
        logger.warning(f"Slack notification failed (non-fatal): {e}")
        return promotion_approval_slack_ts or ""


def write_xcom(payload: dict) -> None:
    xcom_dir = "/airflow/xcom"
    if os.path.isdir(xcom_dir):
        with open(f"{xcom_dir}/return.json", "w") as f:
            json.dump(payload, f)


def run_training() -> None:
    # Train
    model_name, model_version, model_metrics = train_model(
        model_deployment_workflow_id=dags_environment.MODEL_DEPLOYMENT_WORKFLOW_ID
    )

    # Ask for promotion (name and version and metrics)
    # replace
    model_deployment_workflow = get_deployment_workflow(id=dags_environment.MODEL_DEPLOYMENT_WORKFLOW_ID)
    update_promotion_approval(
        model_name=model_name,
        model_version=model_version,
        model_metrics=model_metrics,
        model_deployment_workflow=model_deployment_workflow
    )
    # # Delete/Replace old trained model and promotion approval
    #
    # # Clean up stale candidates BEFORE posting the promotion message
    # delete_stale_candidates(client, "XGBoost", current_version)
    #
    #
    # write_xcom({"trained": True, "model_version": current_version, "f1": metrics["f1"]})
    # logger.info("Training complete. Awaiting promotion approval.")


if __name__ == "__main__":
    # TODO - need to separate functions here
    # TODO - Check if we can pass this to base settings environment
    action = os.environ.get("PIPELINE_ACTION", "train")
    if action == "promote":
        promote()
    else:
        run_training()