from airflow.sdk import task

from dags.modules.schemas.mlflow import ReplaceExpiredChallengerModelConfigurations, DeleteExpiredRegisteredModelConfigurations
from dags.repositories.mlflow import mlflow_client

@task(task_id="replace_challenger_model")
def replace_challenger_model(**context) -> None:
    configurations = ReplaceExpiredChallengerModelConfigurations.from_context(context)

    mlflow_client.set_registered_model_alias(
        name=configurations.replacement_registered_model_name,
        alias="challenger",
        version=configurations.replacement_registered_model_version_string,
    )

@task(task_id="delete_expired_registered_model")
def delete_expired_registered_model(**context) -> None:
    configurations = DeleteExpiredRegisteredModelConfigurations.from_context(context)

    mlflow_client.delete_model_version(
        name=configurations.expired_registered_model_name,
        version=str(configurations.expired_registered_model_version),
    )