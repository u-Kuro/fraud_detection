from sqlalchemy import create_engine, NullPool
from sqlalchemy.orm import sessionmaker

from services.shared.modules.environment.postgres import postgres_environment

sql_session: sessionmaker = sessionmaker(
    create_engine(
        postgres_environment.DATABASE_URL,
        poolclass=NullPool
    )
)