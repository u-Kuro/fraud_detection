from sqlalchemy import create_engine, Engine

from shared.configs import postgres_config

engine: Engine = create_engine(
    postgres_config.POSTGRES_DB_URL,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=3,
)