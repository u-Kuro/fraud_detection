import psycopg2.extras
from airflow.providers.postgres.hooks.postgres import PostgresHook

from dags.shared.modules.configs.postgres import PostgresConfig

psycopg2.extras.register_uuid()

postgres_hook: PostgresHook = PostgresHook(postgres_conn_id=PostgresConfig.POSTGRES_CONNECTION_ID)