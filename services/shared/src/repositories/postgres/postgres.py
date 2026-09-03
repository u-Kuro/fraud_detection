from sqlalchemy import create_engine, NullPool
from sqlalchemy.orm import sessionmaker

from services.shared.src.modules.environment.postgres import postgres_environment

sql_session: sessionmaker = sessionmaker(
    create_engine(
        url=postgres_environment.DATABASE_URL,
        poolclass=NullPool
    )
)