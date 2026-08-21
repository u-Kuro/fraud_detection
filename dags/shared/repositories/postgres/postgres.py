from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from dags.shared.modules.configs.postgres import PostgresConfig

sql_session: sessionmaker = sessionmaker(
    PostgresHook(postgres_conn_id=PostgresConfig.POSTGRES_CONNECTION_ID)
    .get_sqlalchemy_engine(
        engine_kwargs={
            "poolclass": NullPool
        }
    )
)