from sqlalchemy import create_engine, Engine

from services.shared.modules.configs import PostgresConfig

engine: Engine = create_engine(
    PostgresConfig.POSTGRES_DB_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)