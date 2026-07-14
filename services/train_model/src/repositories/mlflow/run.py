import os
import shutil
import tempfile
from contextlib import contextmanager
from typing import Any

import mlflow
import pyarrow as pa
import pyarrow.parquet as pq
from matplotlib.figure import Figure
from pandas import DataFrame

from services.shared.modules.configs import mlflow_config
from services.train_model.src.modules.configs.mlflow import mlflow_artifacts_config
from services.train_model.src.repositories.mlflow.mlflow import mlflow_client

@contextmanager
def transactional_mlflow_run(run_name: str):
    with mlflow.start_run(run_name=run_name) as run:
        try: yield
        except:
            run_id_str = str(run.info.run_id)
            mlflow.delete_run(run_id_str)
            try:
                items = mlflow_client.search_model_versions(f"run_id='{run_id_str}'")
                for item in items:
                    mlflow_client.delete_model_version(
                        name=item.name,
                        version=item.version,
                    )
            except: pass
            raise RuntimeError("Model training failed.")

def save_model_reference_dataset(
    mlflow_model_run_id: str,
    model_reference_dataset: DataFrame
) -> None:
    temporary_directory = tempfile.mkdtemp()
    try:
        dataset_reference_file_path = os.path.join(
            temporary_directory,
            mlflow_artifacts_config.reference_dataset_filename
        )
        pq.write_table(
            table=pa.table(model_reference_dataset),
            where=dataset_reference_file_path
        )
        mlflow.log_artifact(
            local_path=dataset_reference_file_path,
            artifact_path=mlflow_config.REFERENCE_DATASET_PATH,
            run_id=mlflow_model_run_id
        )
    finally:
        shutil.rmtree(temporary_directory)

def save_model_hyperparameters(
        mlflow_model_run_id: str,
        model_hyperparameters: dict[str, Any]
) -> None:
    mlflow.log_params(
        params=model_hyperparameters,
        synchronous=True,
        run_id=mlflow_model_run_id
    )

def save_model_metrics(
        mlflow_model_run_id: str,
        mlflow_model_id: str,
        model_metrics: dict[str, Any],
        model_metric_figures: dict[str, Figure]
) -> None:
    mlflow.log_metrics(
        metrics=model_metrics,
        synchronous=True,
        run_id=mlflow_model_run_id,
        model_id=mlflow_model_id,
    )

    save_model_metric_figures(model_metric_figures)

def save_model_metric_figures(
    model_metric_figures: dict[str, Figure]
) -> None:
    for name, figure in model_metric_figures.items():
        mlflow.log_figure(
            figure=figure,
            artifact_file=f"{name}.png"
        )
