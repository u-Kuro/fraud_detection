from sqlalchemy import create_engine, QueuePool
from sqlalchemy.orm import sessionmaker

from services.shared.src.modules.environment.postgres import postgres_environment

sql_session: sessionmaker = sessionmaker(
    create_engine(
        postgres_environment.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )
)