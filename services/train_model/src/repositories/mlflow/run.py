import os
import shutil
import tempfile
from contextlib import contextmanager
from typing import Any

import pyarrow
from matplotlib.figure import Figure
from pandas import DataFrame
from pyarrow import parquet

from services.shared.src.modules.configs.mlflow import MLflowConfig
from services.shared.src.repositories import mlflow_client, mlflow_module

@contextmanager
def transactional_mlflow_run(run_name: str):
    with mlflow_module.start_run(run_name=run_name) as run:
        try: yield
        except:
            run_id_str = str(run.info.run_id)
            mlflow_client.delete_run(run_id=run_id_str)
            try:
                items = mlflow_client.search_model_versions(filter_string=f"run_id='{run_id_str}'")
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
            MLflowConfig.reference_dataset_file_name
        )
        parquet.write_table(
            table=pyarrow.Table.from_pandas(
                df=model_reference_dataset,
                preserve_index=False
            ),
            where=dataset_reference_file_path
        )
        mlflow_module.log_artifact(
            local_path=dataset_reference_file_path,
            artifact_path=MLflowConfig.reference_dataset_path,
            run_id=mlflow_model_run_id
        )
    finally:
        shutil.rmtree(temporary_directory)

def save_model_hyperparameters(
    mlflow_model_run_id: str,
    model_hyperparameters: dict[str, Any]
) -> None:
    mlflow_module.log_params(
        params=model_hyperparameters,
        synchronous=True,
        run_id=mlflow_model_run_id
    )

def save_model_metrics(
    mlflow_model_run_id: str,
    mlflow_model_id: str,
    model_metrics: dict[str, float],
    model_metric_figures: dict[str, Figure]
) -> None:
    mlflow_module.log_metrics(
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
        mlflow_module.log_figure(
            figure=figure,
            artifact_file=f"{name}.png"
        )