from airflow.providers.postgres.hooks.postgres import PostgresHook

from dags.shared.modules.configs.postgres import PostgresConfig

postgres_hook: PostgresHook = PostgresHook(postgres_conn_id=PostgresConfig.POSTGRES_CONNECTION_ID)