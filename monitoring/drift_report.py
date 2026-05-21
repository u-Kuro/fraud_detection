"""
monitoring/drift_report.py — Evidently data drift + quality report

Reads the last N days of inference logs from Postgres, compares them
against your training-era data (window recorded by record_training_cutoff.py),
and saves an HTML report and latest_drift.json.

The JSON output is consumed by:
  - compare_models.py  → included in the promotion review report
  - drift.yml          → threshold check to auto-trigger retraining

Exit codes:
  0 — success, no drift above threshold
  2 — drift detected above threshold (drift.yml uses this to trigger retraining)
  1 — error / not enough rows

Usage:
    uv run python monitoring/drift_report.py
    uv run python monitoring/drift_report.py --days 7 --min-rows 50
"""
import argparse, logging, json, sys
from datetime import datetime, timedelta, timezone
from os import environ
from pathlib import Path

import pandas as pd
from evidently import BinaryClassification, DataDefinition, Dataset, Report
from evidently.presets import ClassificationPreset, DataDriftPreset
from monitoring.schemas import DriftReportArguments
from monitoring.utils import load_environment
from sqlalchemy import create_engine, Engine, text

logger = logging.getLogger(__name__)

def main() -> None:
    arguments = _get_arguments()

    load_environment()
    engine = create_engine(
        f"postgresql://{environ['POSTGRES_USER']}:{environ['POSTGRES_PASSWORD']}"
        f"@{environ['POSTGRES_HOST']}:{environ['POSTGRES_PORT']}/{environ['FRAUD_DETECTION_DB']}"
    )

    # Get reference window from model training metadata
    ref_start, ref_end = _get_reference_window(engine)
    if ref_start is None or ref_end is None:
        print(
            "ERROR: model_training_metadata is empty. "
            "Run train.yml at least once to populate it.",
            file=sys.stderr,
        )
        sys.exit(1)

    logger.info(f"Reference window: {ref_start} → {ref_end}")

    # Get current window (last N days of inferences)
    current_start = datetime.now(timezone.utc) - timedelta(days=arguments.days)
    logger.info(f"Current window: last {arguments.days} days (since {current_start.date()})")

    df_reference = _get_window_data(engine, ref_start, ref_end)
    df_current = _get_window_data(engine, current_start, datetime.now(timezone.utc))

    logger.info(f"Reference rows: {len(df_reference):,} | Current rows: {len(df_current):,}")

    if len(df_reference) < arguments.minimum_rows:
        print(
            f"ERROR: Only {len(df_reference)} reference rows. Need at least {arguments.minimum_rows}.",
            file=sys.stderr,
        )
        sys.exit(1)

    if len(df_current) < arguments.minimum_rows:
        print(
            f"ERROR: Only {len(df_current)} current rows. Need at least {arguments.minimum_rows}. "
            "Wait for more inference logs to accumulate.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Run Evidently report
    label_columns = {"is_fraud", "is_fraud_prediction", "is_fraud_probability"}
    feature_columns = [c for c in df_reference.columns if c not in label_columns]

    data_definition = DataDefinition(
        classification=[
            BinaryClassification(
                target="is_fraud",
                prediction_labels="is_fraud_prediction",
                prediction_probas="is_fraud_probability",
                labels={0: "Legitimate", 1: "Fraud"},
            )
        ],
        numerical_columns=feature_columns,
    )

    reference_dataset = Dataset.from_pandas(df_reference, data_definition=data_definition)
    current_dataset = Dataset.from_pandas(df_current, data_definition=data_definition)

    report = Report(metrics=[DataDriftPreset(), ClassificationPreset()])
    result = report.run(reference_data=reference_dataset, current_data=current_dataset)

    # Save outputs
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    html_path = reports_dir / f"drift_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html"
    result.save_html(str(html_path))
    logger.info(f"HTML report saved: {html_path}")

    # Save latest_drift.json (used by CI workflows)
    result_dict = result.dict()
    drift_metrics = _extract_drift_summary(result_dict, feature_columns)

    json_path = reports_dir / "latest_drift.json"
    json_path.write_text(json.dumps(drift_metrics, indent=2))
    logger.info(f"JSON summary saved: {json_path}")
    logger.info(
        f"Drift summary: {drift_metrics['drifted_columns']}/{drift_metrics['total_columns']} "
        f"features drifted ({drift_metrics['share_drifted']:.1%})"
    )

    # Exit code for CI threshold check
    if drift_metrics["share_drifted"] > arguments.drift_threshold:
        logger.info(
            f"DRIFT DETECTED: {drift_metrics['share_drifted']:.1%} > "
            f"threshold {arguments.drift_threshold:.1%}"
        )
        sys.exit(2) # drift.yml checks for this exit code

    print(f"No significant drift (below {arguments.drift_threshold:.1%} threshold).")

def _get_reference_window(engine: Engine) -> tuple:
    """Read training data timestamps from model_training_metadata."""
    with engine.connect() as conn:
        row = conn.execute(
            text("""
                SELECT data_start_timestamp, data_end_timestamp
                FROM model_training_metadata
                ORDER BY training_timestamp, metadata_id DESC
                LIMIT 1
            """)
        ).fetchone()
    if row is None:
        return None, None
    else:
        return row[0], row[1]

def _get_window_data(
    engine: Engine,
    start: datetime,
    end: datetime
) -> pd.DataFrame:
    query = f"""
        SELECT DISTINCT ON (transaction_id)
            transaction_timestamp,
            amount,
            {",".join([f"v{i}" for i in range(1, 29)])},
            is_fraud::INTEGER,
            is_fraud_prediction::INTEGER,
            is_fraud_probability
        FROM transaction_inferences
        WHERE transaction_timestamp BETWEEN :start AND :end
        ORDER BY transaction_timestamp, inference_timestamp
    """
    return pd.read_sql(text(query), engine, params={"start": start, "end": end})

def _extract_drift_summary(
    result_dict: dict,
    feature_columns: list
) -> dict:
    """Pull per-feature drift flags out of the Evidently result dict."""
    drifted = []
    try:
        for metric in result_dict.get("metrics", []):
            # DataDriftPreset populates per-column drift results
            if "drift_by_columns" in metric.get("result", {}):
                for col, info in metric["result"]["drift_by_columns"].items():
                    if col in feature_columns and info.get("drift_detected", False):
                        drifted.append(col)
                break
    except Exception as exception:
        print(
            f"ERROR: Failed to parse result - {exception}. "
            f"{result_dict}",
            file=sys.stderr,
        )
        sys.exit(1)

    return {
        "share_drifted": len(drifted) / len(feature_columns) if feature_columns else 0.0,
        "drifted_columns": len(drifted),
        "total_columns": len(feature_columns),
        "drifted_feature_names": drifted,
    }


def _get_arguments() -> DriftReportArguments:
    parser = argparse.ArgumentParser(description="Generate Evidently drift report")
    field_info = DriftReportArguments.model_fields

    days_field_info = field_info["days"]
    parser.add_argument(
        "--days",
        type=days_field_info.annotation,
        default=days_field_info.default,
        help=f"{days_field_info.description}"
             f" (default: {days_field_info.default})"
    )

    minimum_rows_field_info = field_info["minimum_rows"]
    parser.add_argument(
        "--min-rows",
        type=minimum_rows_field_info.annotation,
        default=minimum_rows_field_info.default,
        help=f"{minimum_rows_field_info.description}"
             f" (default: {minimum_rows_field_info.default})"
    )

    drift_threshold_field_info = field_info["drift_threshold"]
    parser.add_argument(
        "--threshold",
        type=drift_threshold_field_info.annotation,
        default=drift_threshold_field_info.default,
        help=f"{drift_threshold_field_info.description}"
             f" (default: {drift_threshold_field_info.default})"
    )

    args = parser.parse_args()

    return DriftReportArguments(
        days=args.days,
        minimum_rows=args.min_rows,
        drift_threshold=args.threshold,
    )

if __name__ == "__main__":
    main()
