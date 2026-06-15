"""
Promotion steps — called when a human approves the candidate.
Steps are idempotent (safe to re-run after crash).

1. begin_promoting() — DB intent record (crash-safe checkpoint)
2. save_permanent_dataset() — copy artifact parquet to permanent path in SeaweedFS
3. mlflow alias moves: candidate→production, old production→archived
4. overwrite_reference_dataset() — update drift_monitor's reference
5. finalize_promotion() — DB finalization (delete pipeline_state, set status=active)
"""

import mlflow
from mlflow import MlflowClient

from services.training_pipeline.src.modules.environment import environment
from services.training_pipeline.src.repositories.postgres.postgres import engine
from services.training_pipeline.src.repositories.postgres.pipeline_state import (
    get_current_state,
    begin_promoting,
    finalize_promotion,
)
from services.training_pipeline.src.repositories.s3.s3 import (
    make_s3,
    save_permanent_dataset,
    overwrite_reference_dataset,
)
from services.shared.logging import logger


def promote() -> None:
    state = get_current_state(engine)
    if state is None or state["state"] not in ("train_pending", "promoting"):
        raise RuntimeError(f"Cannot promote: unexpected pipeline_state={state}")

    run_id: str = state["run_id"]
    model_version: int = state["model_version"]
    dataset_min_date = state["dataset_min_date"]
    dataset_max_date = state["dataset_max_date"]

    mlflow.set_tracking_uri(environment.MLFLOW_TRACKING_URI)
    client = MlflowClient()

    # Infer model_name from the registered model version
    versions = client.search_model_versions(f"run_id='{run_id}'")
    if not versions:
        raise RuntimeError(f"No model version found for run_id={run_id}")
    mv = versions[0]
    model_name: str = mv.name

    # Step 1 — Intent record (idempotent: ON CONFLICT DO UPDATE)
    begin_promoting(
        engine, run_id, model_name, model_version, dataset_min_date, dataset_max_date
    )

    # Step 2 — Download artifact parquet from MLflow and save to permanent SeaweedFS path
    s3 = make_s3()
    import tempfile
    import os

    local_dir = tempfile.mkdtemp()
    artifact_path = mlflow.artifacts.download_artifacts(
        run_id=run_id, artifact_path="dataset", dst_path=local_dir
    )
    # artifact_path is a directory containing the .parquet file
    parquet_files = [f for f in os.listdir(artifact_path) if f.endswith(".parquet")]
    if not parquet_files:
        raise RuntimeError("No parquet artifact found on MLflow run.")

    import pyarrow.parquet as pq

    table = pq.read_table(os.path.join(artifact_path, parquet_files[0]))
    save_permanent_dataset(s3, table, model_name, model_version)  # idempotent

    # Step 3 — MLflow alias rotation (idempotent)
    try:
        client.delete_registered_model_alias(model_name, "production")
    except Exception:
        pass  # no current production alias
    try:
        old_prod = client.get_model_version_by_alias(model_name, "production")
        client.set_registered_model_alias(model_name, "archived", old_prod.version)
    except Exception:
        pass
    client.set_registered_model_alias(model_name, "production", str(model_version))
    try:
        client.delete_registered_model_alias(model_name, "candidate")
    except Exception:
        pass

    # Step 4 — Overwrite reference dataset (idempotent)
    overwrite_reference_dataset(s3, table)

    # Step 5 — Finalization (atomic DB commit)
    finalize_promotion(engine, model_name, model_version)

    logger.info(f"Promotion complete: {model_name} v{model_version}")
