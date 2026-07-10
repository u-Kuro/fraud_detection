from airflow.providers.standard.operators.empty import EmptyOperator

def no_action() -> EmptyOperator:
    return EmptyOperator(task_id=no_action.__name__)