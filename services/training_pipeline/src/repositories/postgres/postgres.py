from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import NullPool

from services.shared.modules.configs import postgres_config

engine: Engine = create_engine(
    postgres_config.POSTGRES_DB_URL,
    poolclass=NullPool
)