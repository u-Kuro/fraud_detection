from services.training_pipeline.src.modules.environment import environment
from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import NullPool

engine: Engine = create_engine(
    environment.POSTGRES_FRAUD_DB_URL,
    poolclass=NullPool
)