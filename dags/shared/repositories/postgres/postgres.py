import psycopg2.extras
from airflow.providers.postgres.hooks.postgres import PostgresHook

from dags.shared.modules.configs.postgres import PostgresConfig

psycopg2.extras.register_uuid()

postgres_hook: PostgresHook = PostgresHook(postgres_conn_id=PostgresConfig.POSTGRES_CONNECTION_ID)

# TODO - 29/07/2026 - Continue here... Apply sqlalchemy ORM in dags...