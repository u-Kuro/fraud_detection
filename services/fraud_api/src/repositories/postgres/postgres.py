from sqlalchemy import create_engine, Engine

from services.training_pipeline.src.modules.config import postgres_config

engine: Engine = create_engine(
    postgres_config.POSTGRES_DB_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)