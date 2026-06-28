import json, os, sys, tempfile
from datetime import datetime, timezone

import mlflow
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import xgboost as xgb
import optuna
import slack_sdk
from mlflow import MlflowClient
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sqlalchemy import text

from services.training_pipeline.src.modules.configs import training_config
from services.training_pipeline.src.repositories.postgres.postgres import engine
from services.training_pipeline.src.repositories.postgres.model_deployment_workflows import (
    get_current_state,
    get_latest_deployed_max_date,
    update_after_training,
    update_promote_slack_ts,
)
from services.training_pipeline.src.services.promote import promote
from shared.modules.configs import fraud_classifier_config, mlflow_config
from shared.modules.environment import slack_environment
from shared.modules.logging import logger

def load_data() -> pd.DataFrame:
    cutoff = get_latest_deployed_max_date()
    with engine.connect() as connection:
        df = pd.read_sql(text(f"""
            SELECT transaction_timestamp, amount,
               {', '.join([f'v{i}' for i in range(1, 29)])},
               is_fraud
            FROM transaction_inferences
            WHERE inference_timestamp > :cutoff
                AND is_fraud IS NOT NULL
            ORDER BY random()
            LIMIT :limit
        """),
        connection,
        params={
            "cutoff": cutoff,
            "limit": training_config.MAXIMUM_TRAINING_DATASET_ROWS
        })
    df["transaction_timestamp"] = df["transaction_timestamp"].apply(lambda x: int(x.timestamp()))
    return df

def train(df: pd.DataFrame):
    x = df[fraud_classifier_config.FRAUD_CLASSIFIER_FEATURES].values
    y = df[fraud_classifier_config.FRAUD_CLASSIFIER_LABEL].astype(int).values
    x_train, x_test, y_train, y_test = train_test_split(
        x, y,
        test_size=training_config.TEST_SIZE,
        random_state=training_config.RANDOM_STATE,
        stratify=y
    )

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators":     trial.suggest_int("n_estimators", 100, 500),
            "max_depth":        trial.suggest_int("max_depth", 3, 8),
            "learning_rate":    trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "subsample":        trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "scale_pos_weight": (y_train == 0).sum() / max((y_train == 1).sum(), 1),
            "random_state":     training_config.RANDOM_STATE,
        }
        model = xgb.XGBClassifier(**params)
        model.fit(x_train, y_train, eval_set=[(x_test, y_test)], verbose=False)
        return f1_score(y_test, model.predict(x_test))

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="maximize")
    study.optimize(
        objective,
        n_trials=training_config.BAYES_STEPS,
        timeout=training_config.TRAINING_TIMEOUT_SECONDS
    )

    best = xgb.XGBClassifier(
        **study.best_params,
        random_state=training_config.RANDOM_STATE
    )
    best.fit(x_train, y_train)
    metrics = {
        "f1": f1_score(y_test, best.predict(x_test)),
        "roc_auc": roc_auc_score(y_test, best.predict_proba(x_test)[:, 1]),
    }
    return best, metrics, study.best_params

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
    promote_slack_ts: str | None,
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
        if promote_slack_ts:
            response = slack.chat_update(
                channel=slack_environment.SLACK_CHANNEL_ID,
                ts=promote_slack_ts,
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
        return promote_slack_ts or ""


def write_xcom(payload: dict) -> None:
    xcom_dir = "/airflow/xcom"
    if os.path.isdir(xcom_dir):
        with open(f"{xcom_dir}/return.json", "w") as f:
            json.dump(payload, f)


def run_training() -> None:
    df = load_data()
    if len(df) < training_config.MINIMUM_TRAINING_DATASET_ROWS:
        logger.error(f"Insufficient labelled data ({len(df)} rows). Exiting.")
        sys.exit(1)

    logger.info(f"Training on {len(df)} rows.")
    mlflow.set_tracking_uri(mlflow_config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(mlflow_config.MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run() as run:
        model, metrics, best_params = train(df)
        mlflow.log_params(best_params)
        mlflow.log_metrics(metrics)

        table = pa.table(df)
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as file:
            pq.write_table(table, file.name)
            mlflow.log_artifact(file.name, artifact_path="dataset")

        transaction_timestamps = df["transaction_timestamp"]

        raw_min = transaction_timestamps.min()
        raw_max = transaction_timestamps.max()

        if not isinstance(raw_min, (int, float)) or not isinstance(raw_max, (int, float)):
            raise ValueError("transaction_timestamp column is empty or all-null.")

        dataset_min = datetime.fromtimestamp(int(raw_min), tz=timezone.utc)
        dataset_max = datetime.fromtimestamp(int(raw_max), tz=timezone.utc)

        mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name="XGBoost")
        client   = MlflowClient()
        versions = client.search_model_versions(f"run_id='{run.info.run_id}'")
        if not versions:
            raise RuntimeError("Model registration failed.")
        model_version = versions[0]
        client.set_registered_model_alias("XGBoost", "candidate", model_version.version)
        logger.info(f"Registered XGBoost v{model_version.version} as 'candidate'.")

    current_version = int(model_version.version)
    update_after_training(str(run.info.run_id), current_version, dataset_min, dataset_max)

    # Clean up stale candidates BEFORE posting the promotion message
    delete_stale_candidates(client, "XGBoost", current_version)

    state = get_current_state()
    promote_slack_ts = (state or {}).get("promote_slack_ts", None)
    slack_ts = post_or_update_promotion_slack(promote_slack_ts, "XGBoost", current_version, metrics)
    if slack_ts:
        update_promote_slack_ts(slack_ts)

    write_xcom({"trained": True, "model_version": current_version, "f1": metrics["f1"]})
    logger.info("Training complete. Awaiting promotion approval.")


if __name__ == "__main__":
    # TODO - need to separate functions here
    # TODO - Check if we can pass this to base settings environment
    action = os.environ.get("PIPELINE_ACTION", "train")
    if action == "promote":
        promote()
    else:
        run_training()