"""
Promotion steps — idempotent (safe to re-run after crash).

1. begin_promoting()          — DB intent record
2. save_permanent_dataset()   — copy artifact parquet to permanent S3 path
3. MLflow alias rotation      — candidate → production, old production → archived
4. overwrite_reference_dataset() — update drift_monitor's reference
5. finalize_promotion()       — DB finalization (delete pipeline_state, set status=active)
6. fraud_api reload           — hot-reload the production model (zero-downtime)
"""

import os
import tempfile

import httpx
import mlflow
import pyarrow.parquet as pq
from mlflow import MlflowClient

from services.training_pipeline.src.modules.environment import environment
from services.training_pipeline.src.repositories.postgres.postgres import engine
from services.training_pipeline.src.repositories.postgres.pipeline_state import (
    get_current_state,
    begin_promoting,
    finalize_promotion,
)
from services.training_pipeline.src.repositories.s3.s3 import (
    save_permanent_dataset,
    overwrite_reference_dataset,
)
from shared.logging import logger


def promote() -> None:
    state = get_current_state()
    if state is None or state["state"] not in ("train_pending", "promoting"):
        raise RuntimeError(f"Cannot promote: unexpected pipeline_state={state}")

    run_id:          str      = state["run_id"]
    model_version:   int      = state["model_version"]
    dataset_min_date          = state["dataset_min_date"]
    dataset_max_date          = state["dataset_max_date"]

    mlflow.set_tracking_uri(environment.MLFLOW_TRACKING_URI)
    client = MlflowClient()

    versions = client.search_model_versions(f"run_id='{run_id}'")
    if not versions:
        raise RuntimeError(f"No model version found for run_id={run_id}")
    mv         = versions[0]
    model_name = mv.name

    # Step 1 — Intent record
    begin_promoting(run_id, model_name, model_version, dataset_min_date, dataset_max_date)

    # Step 2 — Download training artifact and save to permanent path
    local_dir = tempfile.mkdtemp()
    artifact_path = mlflow.artifacts.download_artifacts(
        run_id=run_id, artifact_path="dataset", dst_path=local_dir
    )
    parquet_files = [f for f in os.listdir(artifact_path) if f.endswith(".parquet")]
    if not parquet_files:
        raise RuntimeError("No parquet artifact found on MLflow run.")
    table = pq.read_table(os.path.join(artifact_path, parquet_files[0]))
    save_permanent_dataset(table, model_name, model_version)

    # Step 3 — MLflow alias rotation (idempotent)
    try:
        old_prod = client.get_model_version_by_alias(model_name, "production")
        client.set_registered_model_alias(model_name, "archived", old_prod.version)
    except Exception:
        pass
    try:
        client.delete_registered_model_alias(model_name, "production")
    except Exception:
        pass
    client.set_registered_model_alias(model_name, "production", str(model_version))
    try:
        client.delete_registered_model_alias(model_name, "candidate")
    except Exception:
        pass

    # Step 4 — Overwrite reference dataset
    overwrite_reference_dataset(table)

    # Step 5 — Finalization
    finalize_promotion(model_name, model_version)
    logger.info(f"Promotion complete: {model_name} v{model_version}")

    # Step 6 — Hot-reload fraud_api (zero-downtime: the new model is already in MLflow
    # under the 'production' alias; fraud_api just re-fetches it)
    try:
        resp = httpx.post(
            f"{environment.FRAUD_API_URL}/internal/reload-model",
            timeout=30.0,
        )
        resp.raise_for_status()
        logger.info("fraud_api model reload triggered successfully.")
    except Exception as e:
        logger.warning(
            f"Could not trigger fraud_api reload (non-fatal — next pod restart will pick up new model): {e}"
        )