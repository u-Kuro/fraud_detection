from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.shared.modules.configs.postgres import PostgresConfig

sql_session: sessionmaker = sessionmaker(
    create_engine(
        PostgresConfig.POSTGRES_DB_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
)