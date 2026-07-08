from airflow.providers.postgres.hooks.postgres import PostgresHook

from dags.modules.configs import postgres_config

postgres_hook: PostgresHook = PostgresHook(postgres_conn_id=postgres_config.SLACK_CONNECTION_ID)