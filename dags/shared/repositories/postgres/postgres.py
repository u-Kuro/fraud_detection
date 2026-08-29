from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from dags.shared.modules.environment.postgres import postgres_environment

sql_session: sessionmaker = sessionmaker(
    PostgresHook(postgres_conn_id=postgres_environment.POSTGRES_CONNECTION_ID)
    .get_sqlalchemy_engine(
        engine_kwargs={
            "poolclass": NullPool
        }
    )
)