# Drift Monitoring examples
import argparse
import io
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from evidently import BinaryClassification, DataDefinition, Dataset, Report
from evidently.presets import ClassificationPreset, DataDriftPreset

def get_reference_window(engine) -> tuple:
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT data_start_timestamp, data_end_timestamp
        """)).fetchone()

    if row:
        return (
            row[0].astimezone(timezone.utc),
            row[1].astimezone(timezone.utc)
        )
    else:
        return (None, None)

def get_window_data_sqlalchemy(
    engine,
    start: datetime,
) -> pd.DataFrame:
    query = text(f"""
        WITH selected AS (
            SELECT DISTINCT ON (transaction_id)
                transaction_timestamp,
                amount,
                {", ".join([f"v{i}" for i in range(1, 29)])},
                is_fraud::INTEGER AS is_fraud,
                is_fraud_prediction::INTEGER AS is_fraud_prediction,
                is_fraud_probability
            FROM transaction_inferences
            WHERE transaction_timestamp >= :start
            ORDER BY 
                transaction_id DESC,
                transaction_timestamp DESC,
                inference_timestamp DESC 
        )
        SELECT * 
        FROM selected
        ORDER BY random()
        LIMIT :max_selected_rows
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={
            "start": start,
            "max_selected_rows": environment.MAX_SELECTED_ROWS
        })

def extract_drift_summary(
    result_dict: dict,
    feature_columns: list[str],
    ref_start: datetime | None = None,
    ref_end: datetime | None = None,
    current_start: datetime | None = None,
) -> dict:
    data_drift: dict = {}
    concept_drift: dict = {}

    for metric in result_dict.get("metrics", []):
        metric_name = metric.get("metric", "")
        result = metric.get("result", {})

        # Data drift — feature distribution shift P(X)
        if "drift_by_columns" in result:
            drifted = [
                col
                for col, info in result["drift_by_columns"].items()
                if col in feature_columns and info.get("drift_detected", False)
            ]
            data_drift = {
                "dataset_drift_detected": result.get("dataset_drift", False),
                "share_drifted_features": result.get("share_drifted_features", 0.0),
                "number_of_drifted_features": result.get("number_of_drifted_features", 0),
                "total_features": result.get("number_of_columns", len(feature_columns)),
                "drifted_feature_names": drifted,
            }

        # Concept / model performance drift — P(Y|X) degradation
        if metric_name == "ClassificationQualityMetric" and "current" in result and "reference" in result:
            cur = result["current"]
            ref = result["reference"]

            def _delta(key: str) -> float | None:
                c, r = cur.get(key), ref.get(key)
                return round(c - r, 4) if c is not None and r is not None else None

            concept_drift = {
                "f1_current": cur.get("f1"),
                "f1_reference": ref.get("f1"),
                "f1_delta": _delta("f1"),
                "roc_auc_current": cur.get("roc_auc"),
                "roc_auc_reference": ref.get("roc_auc"),
                "roc_auc_delta": _delta("roc_auc"),
                "precision_delta": _delta("precision"),
                "recall_delta": _delta("recall"),
                # A negative delta means the model performs worse on current data.
                # Flag concept drift if F1 degrades by more than 5 pp.
                "concept_drift_detected": (
                    _delta("f1") is not None and _delta("f1") < -0.05
                ),
            }

    return {
        # Top-level shortcut used by drift.yaml threshold check
        "share_drifted_features": data_drift.get("share_drifted_features", 0.0),
        # Data drift (P(X) shift)
        "data_drift": data_drift,
        # Concept drift (P(Y|X) shift: model quality on current data vs reference)
        "concept_drift": concept_drift,
        # Windows
        "reference_start": ref_start.isoformat() if ref_start else None,
        "reference_end": ref_end.isoformat() if ref_end else None,
        "current_start": current_start.isoformat() if current_start else None,
        "recommended_retrain_data_start": ref_end.isoformat() if ref_end else None,
    }

def upload_reports_to_seaweedfs(
    html_content: bytes,
    drift_metrics: dict,
    ts_label: str,
) -> tuple[str, str]:
    s3 = boto3.client(
        "s3",
        endpoint_url=environment.SEAWEEDFS_S3_URL,
        aws_access_key_id=environment.SEAWEEDFS_ACCESS_KEY,
        aws_secret_access_key=environment.SEAWEEDFS_SECRET_KEY,
    )
    try:
        s3.head_bucket(Bucket=environment.SEAWEEDFS_REPORTS_BUCKET)
    except:
        s3.create_bucket(Bucket=environment.SEAWEEDFS_REPORTS_BUCKET)

    html_key = f"drift_{ts_label}.html"
    json_key = f"drift_{ts_label}.json"
    s3.upload_fileobj(io.BytesIO(html_content), environment.SEAWEEDFS_REPORTS_BUCKET, html_key)
    s3.put_object(
        Bucket=environment.SEAWEEDFS_REPORTS_BUCKET,
        Key=json_key,
        Body=json.dumps(drift_metrics, indent=2).encode(),
        ContentType="application/json",
    )
    return html_key, json_key

def get_arguments() -> DriftReportArguments:
    fields = DriftReportArguments.model_fields
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=fields["days"].default)
    parser.add_argument("--min-rows", type=int, default=fields["minimum_rows"].default)
    parser.add_argument("--threshold", type=float, default=fields["drift_threshold"].default)
    args = parser.parse_args()
    return DriftReportArguments(days=args.days, minimum_rows=args.min_rows, drift_threshold=args.threshold)

def main() -> None:
    # If theres no deployed model skip to training (just a seeder thing)
    arguments = get_arguments()
    engine = create_engine(
        f"postgresql://{environment.POSTGRES_USER}:{environment.POSTGRES_PASSWORD}"
        f"@{environment.POSTGRES_HOST}:{environment.POSTGRES_PORT}/{environment.FRAUD_DETECTION_DB_NAME}",
        poolclass=NullPool,
    )

    ref_start, ref_end = get_reference_window(engine)
    if ref_start is None or ref_end is None:
        sys.exit(1)

    current_start = datetime.now(timezone.utc) - timedelta(days=arguments.days)

    df_reference = # get from seaweedfs parqueet data from last trained model
    ref_count = len(df_reference)

    df_current = get_window_data_sqlalchemy(engine, current_start)
    cur_count = len(df_current)

    if ref_count < arguments.minimum_rows:
        sys.exit(1)
    if cur_count < arguments.minimum_rows:
        sys.exit(1)

    label_cols = {"is_fraud", "is_fraud_prediction", "is_fraud_probability", "transaction_timestamp"}
    feature_columns = [c for c in df_reference.columns if c not in label_cols]

    data_definition = DataDefinition(
        classification=[BinaryClassification(
            target="is_fraud",
            prediction_labels="is_fraud_prediction",
            prediction_probas="is_fraud_probability",
            labels={0: "Legitimate", 1: "Fraud"},
        )],
        numerical_columns=feature_columns,
    )

    reference_dataset = Dataset.from_pandas(df_reference, data_definition=data_definition)
    current_dataset = Dataset.from_pandas(df_current, data_definition=data_definition)

    report = Report(metrics=[DataDriftPreset(), ClassificationPreset()])
    result = report.run(
        reference_data=reference_dataset,
        current_data=current_dataset
    )

    ts_label = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_buf = io.StringIO()
    result.save_html(html_buf)
    html_bytes = html_buf.getvalue().encode("utf-8")

    drift_metrics = extract_drift_summary(
        result.dict(), feature_columns,
        ref_start=ref_start, ref_end=ref_end, current_start=current_start,
    )

    # Write JSON locally so it can be read by other part of workflows
    Path("/tmp/latest_drift.json").write_text(json.dumps(drift_metrics, indent=2))

    upload_reports_to_seaweedfs(html_bytes, drift_metrics, ts_label)

    data_drift_detected: bool = drift_metrics["data_drift"].get("dataset_drift_detected", False)
    concept_drift_detected: bool = drift_metrics["concept_drift"].get("concept_drift_detected", False)
    share_drifted: float = drift_metrics["data_drift"].get("share_drifted_features", 0.0)

    if data_drift_detected or concept_drift_detected:
        reasons = []
        if data_drift_detected:
            reasons.append(f"data drift ({share_drifted:.1%} features drifted)")
        if concept_drift_detected:
            f1_delta = drift_metrics["concept_drift"].get("f1_delta", "n/a")
            reasons.append(f"concept drift (F1 delta={f1_delta})")

# Training examples
import logging, math, random, sys
from IPython.display import display
from datetime import datetime, timezone

# Packages
import mlflow, optuna
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from mlflow import MlflowClient
from mlflow.models import infer_signature
from numpy import ndarray
from optuna.samplers import TPESampler
from sklearn.base import BaseEstimator
from sklearn.metrics import (
    f1_score, average_precision_score, recall_score,
    precision_score, roc_auc_score, accuracy_score,
    ConfusionMatrixDisplay
)
from sklearn.model_selection import (
    StratifiedKFold, cross_val_score, train_test_split
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler
from sqlalchemy import create_engine, text
from xgboost import XGBClassifier

def get_last_training_cutoff(engine) -> datetime:
     with engine.connect() as conn:
        val = conn.execute(text("""
            SELECT data_end_timestamp
            FROM model_training_metadata
            ORDER BY
                data_end_timestamp DESC
            LIMIT 1
        """)).scalar()

        return (
            val.astimezone(timezone.utc)
            if val
            # Unix Epoch Time
            else datetime(1970, 1, 1, tzinfo=timezone.utc)
        )

def load_data(
    engine,
    last_training_cutoff: datetime
) -> pd.DataFrame:
    with engine.connect() as conn:
        df = pd.read_sql(
            text(f"""
                WITH selected AS (
                    SELECT DISTINCT ON (transaction_id)
                        EXTRACT(EPOCH FROM transaction_timestamp)::INTEGER AS transaction_timestamp,
                        amount,
                        {", ".join([f"v{i}" for i in range(1, 29)])},
                        is_fraud::INTEGER AS is_fraud,
                    FROM transaction_inferences
                    WHERE transaction_timestamp > :last_training_cutoff
                    ORDER BY
                        transaction_id DESC,
                        transaction_timestamp DESC,
                        inference_timestamp DESC 
                )
                SELECT * 
                FROM selected
                ORDER BY random()
                LIMIT :max_selected_rows
            """),
            conn,
            params={
                "last_training_cutoff": last_training_cutoff,
                "max_selected_rows": environment.MAX_SELECTED_ROWS
            }
        )
    return df

def get_predictions_sklearn(
    model: BaseEstimator,
    x: ndarray,
    threshold: float = 0.5
) -> dict[str, ndarray]:
    y_prob = model.predict_proba(x)[:, 1]
    return {
        "y_pred": (y_prob >= threshold).astype(int),
        "y_prob": y_prob
    }

def evaluate_model_predictions(
    y_pred: ndarray,
    y_prob: ndarray,
    y_true: ndarray
) -> dict:
    return {
        "F1 score": f1_score(y_true, y_pred),
        "PR-AUC": average_precision_score(y_true, y_prob),
        "Recall": recall_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred),
        "ROC-AUC": roc_auc_score(y_true, y_prob),
        "Accuracy": accuracy_score(y_true, y_pred)
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
        y_true, y_pred,
        display_labels=["Legitimate", "Fraud"],
        normalize="true",
        cmap='Blues',
        values_format='.1%',
        ax=confusion_matrix_ax
    )
    confusion_matrix_ax.set_title(title)

    probability_scatter_figure, probability_scatter_ax = plt.subplots()
    probability_scatter_ax.scatter(
        y_prob,
        range(len(y_true)),
        c=np.where(y_true == 1, "red", "blue"),
        edgecolors="k"
    )
    probability_scatter_ax.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=1))
    probability_scatter_ax.axvline(x=threshold, alpha=0.3, color="white", linestyle="--")
    probability_scatter_ax.axvspan(threshold, 1.0, alpha=0.05, color='red')
    probability_scatter_ax.axvspan(0.0, threshold, alpha=0.05, color='blue')
    probability_scatter_ax.set_yticks([])
    probability_scatter_ax.set_ylabel("Transactions")
    probability_scatter_ax.set_xlabel("Fraud Probability Score")
    probability_scatter_ax.set_title(title)

    return {
        f"probability_scatter_{title.lower()}": probability_scatter_figure,
        f"confusion_matrix_{title.lower()}": confusion_matrix_figure,
    }

def main() -> None:
    # Reproducibility
    RANDOM_STATE = environment.RANDOM_STATE
    random.seed(RANDOM_STATE)
    np.random.seed(RANDOM_STATE)

    # Cross Validation
    TEST_SIZE = environment.TEST_SIZE
    VAL_SIZE = environment.VAL_SIZE
    CV_VAL_SPLIT = math.ceil(((1.0 - TEST_SIZE) / VAL_SIZE) - sys.float_info.epsilon)
    CV = StratifiedKFold(n_splits=CV_VAL_SPLIT, shuffle=True, random_state=RANDOM_STATE)

    # Hyperparameter Optimization
    BAYES_STEPS = environment.BAYES_STEPS

    # Optuna
    TRAINING_TIMEOUT_SECONDS = environment.TRAINING_TIMEOUT_SECONDS
    optuna.logging.set_verbosity(optuna.logging.INFO)

    # MLflow
    EXPERIMENT_NAME = environment.TRAINING_EXPERIMENT_NAME
    mlflow.set_tracking_uri(environment.MLFLOW_TRACKING_URI)
    if not mlflow.get_experiment_by_name(EXPERIMENT_NAME):
        mlflow.create_experiment(name=EXPERIMENT_NAME)
    mlflow.set_experiment(EXPERIMENT_NAME)

    engine = create_engine(
        f"postgresql://{environment.POSTGRES_USER}:{environment.POSTGRES_PASSWORD}"
        f"@{environment.POSTGRES_HOST}:{environment.POSTGRES_PORT}/{environment.FRAUD_DETECTION_DB_NAME}"
    )
    last_training_cutoff = get_last_training_cutoff(engine)
    df = load_data(engine, last_training_cutoff=last_training_cutoff)

    row_count = len(df)

    if row_count < environment.TRAINING_MINIMUM_ROWS:
        sys.exit(1)

    data_start_timestamp = datetime.fromtimestamp(int(df["transaction_timestamp"].min()), tz=timezone.utc)
    data_end_timestamp = datetime.fromtimestamp(int(df["transaction_timestamp"].max()), tz=timezone.utc)

    x = df.drop("is_fraud", axis=1)
    y = df["is_fraud"]

    train_x, test_x, train_y, test_y = train_test_split(
        x, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    train_y_positive_weight = (train_y == 0).sum() / (train_y == 1).sum()

    smote = SMOTE(random_state=RANDOM_STATE)
    train_x, train_y = smote.fit_resample(train_x, train_y)

    train_x_np = train_x.values.astype(np.float32)
    train_y_np = train_y.values.ravel().astype(np.int64)
    test_x_np = test_x.values.astype(np.float32)
    test_y_np = test_y.values.ravel().astype(np.int64)

    with mlflow.start_run(run_name="XGBoost") as run:
        try:
            model_name = "xgb"
            run_name_str = str(run.info.run_name)
            run_id_str = str(run.info.run_id)

            def xgb_objective(trial: optuna.Trial) -> float:
                xgb_params = {
                    f"n_estimators": trial.suggest_int(f"n_estimators", 100, 500),
                    f"max_depth": trial.suggest_int(f"max_depth", 3, 10),
                    f"learning_rate": trial.suggest_float(f"learning_rate", 0.005, 0.3, log=True),
                    f"subsample": trial.suggest_float(f"subsample", 0.5, 1.0),
                    f"colsample_bytree": trial.suggest_float(f"colsample_bytree", 0.4, 1.0),
                    f"reg_alpha": trial.suggest_float(f"reg_alpha", 1e-6, 1.0, log=True),
                    f"reg_lambda": trial.suggest_float(f"reg_lambda", 1e-6, 5.0, log=True),
                    f"gamma": trial.suggest_float(f"gamma", 0.0, 5.0),
                    f"min_child_weight": trial.suggest_int(f"min_child_weight", 1, 10),
                }

                return float(np.mean(cross_val_score(
                    Pipeline([
                        ("robust_scaler", RobustScaler()),
                        (model_name,
                         XGBClassifier(
                             **xgb_params, scale_pos_weight=train_y_positive_weight, random_state=RANDOM_STATE,
                             n_jobs=-1, verbosity=2
                         )
                         ),
                    ]),
                    train_x_np,
                    train_y_np,
                    cv=CV,
                    scoring="average_precision",
                    n_jobs=1
                )))

            study = optuna.create_study(
                direction="maximize",
                sampler=TPESampler(seed=RANDOM_STATE, multivariate=True),
            )
            study.optimize(
                xgb_objective,
                n_trials=BAYES_STEPS,
                n_jobs=1,
                show_progress_bar=True,
                gc_after_trial=True,
                timeout=TRAINING_TIMEOUT_SECONDS
            )

            xgb_best_params = study.best_params
            xgb_best_model = Pipeline([
                ("robust_scaler", RobustScaler()),
                (model_name,
                 XGBClassifier(
                     **xgb_best_params, scale_pos_weight=train_y_positive_weight, random_state=RANDOM_STATE,
                     n_jobs=-1, verbosity=2
                 )
                 ),
            ]).fit(train_x_np, train_y_np)

            xgb_predictions = get_predictions_sklearn(xgb_best_model, test_x_np)
            xgb_metrics = evaluate_model_predictions(**xgb_predictions, y_true=test_y_np)
            xgb_figures = visualize_model_predictions(**xgb_predictions, y_true=test_y_np, title=run_name_str)

            display(pd.DataFrame(xgb_metrics.items(), columns=["Metric", "Score"]))

            xgb_model_info = mlflow.sklearn.log_model(
                sk_model=xgb_best_model,
                serialization_format=mlflow.sklearn.SERIALIZATION_FORMAT_SKOPS,
                registered_model_name=run_name_str,
                signature=infer_signature(
                    model_input=test_x_np,
                    model_output=xgb_best_model.predict(test_x_np)
                ),
                input_example=test_x_np[:5],
                pip_requirements=["xgboost==3.2.0", "scikit-learn==1.8.0", "numpy==2.4.6", "pandas==2.3.3"],
                name="model",
                skops_trusted_types=["xgboost.core.Booster", "xgboost.sklearn.XGBClassifier"],
            )
            mlflow.log_params(params=xgb_best_params, run_id=xgb_model_info.run_id)
            mlflow.log_metrics(
                metrics=xgb_metrics,
                run_id=xgb_model_info.run_id,
                model_id=xgb_model_info.model_id
            )
            for name, figure in xgb_figures.items():
                plt.show()
                mlflow.log_figure(figure, f"{name}.png")
                plt.close(figure)

            mlflow.set_tag("data_start_timestamp", data_start_timestamp.isoformat())
            mlflow.set_tag("data_end_timestamp", data_end_timestamp.isoformat())

            with open("mlflow_run_id.txt", "w") as f:
                f.write(run_id_str)

        except:
            run_id_str = str(run.info.run_id)
            logging.error("Failed to train the model", exc_info=True)
            client = MlflowClient()
            mlflow.delete_run(run_id_str)
            try:
                versions = client.search_model_versions(f"run_id='{run_id_str}'")
                for v in versions: client.delete_model_version(name=v.name, version=v.version)
            except:
                logging.error(f"Failed to delete failed run id: '{run_id_str}'", exc_info=True)
            sys.exit(1)

# Archiving examples
import io
import sys
import time

import boto3
import pyarrow as pa
import pyarrow.parquet as pq
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

FEATURES = [f"v{i}" for i in range(1, 29)]
ALL_COLS = [
    "request_id", "inference_timestamp", "transaction_id", "transaction_timestamp",
    "amount", "is_fraud", "is_fraud_prediction", "is_fraud_probability",
    *FEATURES,
]

def get_training_cutoff(engine_read):
    with engine_read.connect() as conn:
        row = conn.execute(text("""
            SELECT data_end_timestamp LIMIT 1
        """)).scalar()
    return row if row else None

def make_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=environment.SEAWEEDFS_S3_URL,
        aws_access_key_id=environment.SEAWEEDFS_ACCESS_KEY,
        aws_secret_access_key=environment.SEAWEEDFS_SECRET_KEY,
    )

def ensure_bucket(s3, bucket: str) -> None:
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        s3.create_bucket(Bucket=bucket)

def archive_batch(
    engine_read,
    engine_write,
    s3,
    cutoff,
    batch_num: int,
) -> ArchivingBatchResult | None:
    from datetime import datetime, timezone
    t0 = time.perf_counter()
    col_list = ", ".join(ALL_COLS)

    with engine_read.connect() as conn:
        rows = conn.execute(text(f"""
            SELECT {col_list} FROM transaction_inferences
            WHERE transaction_timestamp <= :cutoff
            ORDER BY transaction_timestamp, request_id
            LIMIT :batch_size
        """), {"cutoff": cutoff, "batch_size": environment.ARCHIVE_BATCH_SIZE}).fetchall()

    if not rows:
        return None

    columns = {col: [getattr(r, col, None) for r in rows] for col in ALL_COLS}
    buf = io.BytesIO()
    pq.write_table(pa.table(columns), buf)
    buf.seek(0)

    ts_label = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    key = f"batch_{batch_num:06d}_{ts_label}.parquet"
    s3.upload_fileobj(buf, environment.SEAWEEDFS_BUCKET, key)

    request_ids = [r.request_id for r in rows]
    with engine_write.connect() as conn:
        conn.execute(
            text("DELETE FROM transaction_inferences WHERE request_id = ANY(:ids)"),
            {"ids": request_ids},
        )
        conn.commit()

    return ArchivingBatchResult(
        batch_number=batch_num,
        rows_read=len(rows),
        rows_deleted=len(request_ids),
        parquet_key=key,
        cutoff_timestamp=cutoff,
        elapsed_ms=(time.perf_counter() - t0) * 1000,
    )


def main() -> None:
    read_url = (
        f"postgresql://{environment.POSTGRES_USER}:{environment.POSTGRES_PASSWORD}"
        f"@{environment.POSTGRES_HOST}:{environment.POSTGRES_PORT}/{environment.FRAUD_DETECTION_DB_NAME}"
    )
    write_url = (
        f"postgresql://{environment.POSTGRES_USER}:{environment.POSTGRES_PASSWORD}"
        f"@{environment.POSTGRES_HOST}:{environment.POSTGRES_PORT}/{environment.FRAUD_DETECTION_DB_NAME}"
    )
    engine_read = create_engine(read_url, poolclass=NullPool)
    engine_write = create_engine(write_url, poolclass=NullPool)

    cutoff = get_training_cutoff(engine_read)
    if cutoff is None:
        sys.exit(1)

    s3 = make_s3_client()
    ensure_bucket(s3, environment.SEAWEEDFS_BUCKET)

    batch_num = 0
    total_archived = 0
    while True:
        batch_num += 1
        result = archive_batch(engine_read, engine_write, s3, cutoff, batch_num)
        if result is None:
            break
        total_archived += result.rows_deleted
        _batch_rows.record(result.rows_read)
        _rows_deleted.add(result.rows_deleted)
        time.sleep(environment.ARCHIVE_BATCH_SLEEP_MS / 1000)