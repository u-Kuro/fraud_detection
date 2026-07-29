from sqlalchemy import create_engine, NullPool
from sqlalchemy.orm import sessionmaker

from services.shared.modules.configs.postgres import PostgresConfig

sql_session: sessionmaker = sessionmaker(
    create_engine(
        PostgresConfig.POSTGRES_DB_URL,
        poolclass=NullPool
    )
)