from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from services.shared.modules.configs.postgres import PostgresConfig

sql_session: sessionmaker = sessionmaker(
    create_engine(
        url=PostgresConfig.POSTGRES_DB_URL,
        poolclass=NullPool
    )
)