import json
import os
import sys
import tempfile

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

from services.training_pipeline.src.modules.environment import environment
from services.training_pipeline.src.repositories.postgres.postgres import engine
from services.training_pipeline.src.repositories.postgres.pipeline_state import (
    get_current_state,
    get_latest_deployed_max_date,
    update_after_training,
    update_promote_slack_ts,
)
from services.training_pipeline.src.services.promote import promote
from shared.logging import logger

FEATURE_COLS = ["transaction_timestamp", "amount"] + [f"v{i}" for i in range(1, 29)]
TARGET_COL   = "is_fraud"

def _load_data() -> pd.DataFrame:
    cutoff = get_latest_deployed_max_date()
    query  = text(f"""
        SELECT transaction_timestamp, amount,
               {', '.join([f'v{i}' for i in range(1, 29)])},
               is_fraud
        FROM transaction_inferences
        WHERE inference_timestamp > :cutoff
          AND is_fraud IS NOT NULL
        ORDER BY random()
        LIMIT :limit
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"cutoff": cutoff, "limit": environment.MAX_SELECTED_ROWS})
    df["transaction_timestamp"] = df["transaction_timestamp"].apply(lambda x: int(x.timestamp()))
    return df


def _train(df: pd.DataFrame):
    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].astype(int).values
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=environment.TEST_SIZE, random_state=environment.RANDOM_STATE, stratify=y
    )

    def objective(trial: optuna.Trial) -> float:
        params = {
            "n_estimators":     trial.suggest_int("n_estimators", 100, 500),
            "max_depth":        trial.suggest_int("max_depth", 3, 8),
            "learning_rate":    trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "subsample":        trial.suggest_float("subsample", 0.6, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
            "scale_pos_weight": (y_train == 0).sum() / max((y_train == 1).sum(), 1),
            "random_state":     environment.RANDOM_STATE,
        }
        m = xgb.XGBClassifier(**params)
        m.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
        return f1_score(y_test, m.predict(X_test))

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=environment.BAYES_STEPS, timeout=environment.TRAINING_TIMEOUT_SECONDS)

    best = xgb.XGBClassifier(**study.best_params, random_state=environment.RANDOM_STATE)
    best.fit(X_train, y_train)
    metrics = {
        "f1":      f1_score(y_test, best.predict(X_test)),
        "roc_auc": roc_auc_score(y_test, best.predict_proba(X_test)[:, 1]),
    }
    return best, metrics, study.best_params

def _delete_stale_candidates(client: MlflowClient, model_name: str, current_version: int) -> None:
    """Delete MLflow model versions that are trained candidates but will never be promoted."""
    try:
        versions = client.search_model_versions(f"name='{model_name}'")
        for v in versions:
            aliases = getattr(v, "aliases", []) or []
            ver = int(v.version)
            if ver == current_version:
                continue
            # Version has candidate alias on it but is not the new one — remove alias and delete
            if "candidate" in aliases:
                try:
                    client.delete_registered_model_alias(model_name, "candidate")
                except Exception:
                    pass
            # Delete versions that have no aliases and are not in production
            if "production" not in aliases and "archived" not in aliases:
                try:
                    client.delete_model_version(model_name, str(ver))
                    logger.info(f"Deleted stale candidate model version {model_name} v{ver}")
                except Exception as e:
                    logger.warning(f"Could not delete stale version {ver}: {e}")
    except Exception as e:
        logger.warning(f"Stale candidate cleanup failed (non-fatal): {e}")

def _post_or_update_promotion_slack(
    promote_slack_ts: str | None,
    model_name: str,
    model_version: int,
    metrics: dict,
) -> str:
    """Post or update in-place the promotion approval Slack message."""
    slack = slack_sdk.WebClient(token=environment.SLACK_BOT_USER_AUTH_TOKEN)
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": "✅ Training Complete — Approve for Promotion"}},
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
                    "text": {"type": "plain_text", "text": "🚀 Approve Promotion"},
                    "style": "primary",
                    "action_id": "approve_promotion",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "❌ Reject"},
                    "style": "danger",
                    "action_id": "reject_promotion",
                },
            ],
        },
    ]

    try:
        if promote_slack_ts:
            resp = slack.chat_update(
                channel=environment.SLACK_CHANNEL_ID, ts=promote_slack_ts, blocks=blocks
            )
        else:
            resp = slack.chat_postMessage(channel=environment.SLACK_CHANNEL_ID, blocks=blocks)
        return resp["ts"]
    except Exception as e:
        logger.warning(f"Slack notification failed (non-fatal): {e}")
        return promote_slack_ts or ""


def _write_xcom(payload: dict) -> None:
    xcom_dir = "/airflow/xcom"
    if os.path.isdir(xcom_dir):
        with open(f"{xcom_dir}/return.json", "w") as f:
            json.dump(payload, f)


def run_training() -> None:
    df = _load_data()
    if len(df) < environment.TRAINING_MINIMUM_ROWS:
        logger.error(f"Insufficient labelled data ({len(df)} rows). Exiting.")
        sys.exit(1)

    logger.info(f"Training on {len(df)} rows.")
    mlflow.set_tracking_uri(environment.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(environment.MLFLOW_EXPERIMENT_NAME)

    with mlflow.start_run() as run:
        model, metrics, best_params = _train(df)
        mlflow.log_params(best_params)
        mlflow.log_metrics(metrics)

        table = pa.Table.from_pandas(df)
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            pq.write_table(table, f.name)
            mlflow.log_artifact(f.name, artifact_path="dataset")

        ts_col      = df["transaction_timestamp"]
        dataset_min = pd.Timestamp(int(ts_col.min()), unit="s", tz="UTC").to_pydatetime()
        dataset_max = pd.Timestamp(int(ts_col.max()), unit="s", tz="UTC").to_pydatetime()

        mlflow.sklearn.log_model(model, artifact_path="model", registered_model_name="XGBoost")
        client   = MlflowClient()
        versions = client.search_model_versions(f"run_id='{run.info.run_id}'")
        if not versions:
            raise RuntimeError("Model registration failed.")
        mv = versions[0]
        client.set_registered_model_alias("XGBoost", "candidate", mv.version)
        logger.info(f"Registered XGBoost v{mv.version} as 'candidate'.")

    current_version = int(mv.version)
    update_after_training(str(run.info.run_id), current_version, dataset_min, dataset_max)

    # Clean up stale candidates BEFORE posting the promotion message
    _delete_stale_candidates(client, "XGBoost", current_version)

    state    = get_current_state()
    promote_slack_ts = (state or {}).get("promote_slack_ts", None)
    slack_ts = _post_or_update_promotion_slack(promote_slack_ts, "XGBoost", current_version, metrics)
    if slack_ts:
        update_promote_slack_ts(slack_ts)

    _write_xcom({"trained": True, "model_version": current_version, "f1": metrics["f1"]})
    logger.info("Training complete. Awaiting promotion approval.")


if __name__ == "__main__":
    action = os.environ.get("PIPELINE_ACTION", "train")
    if action == "promote":
        promote()
    else:
        run_training()