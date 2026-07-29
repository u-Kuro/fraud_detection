from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import NullPool

from services.shared.modules.configs.postgres import PostgresConfig

engine: Engine = create_engine(
    PostgresConfig.POSTGRES_DB_URL,
    poolclass=NullPool
)