from services.archiving.src.modules.environment import environment
from sqlalchemy import create_engine, Engine

engine: Engine = create_engine(
    environment.postgres_fraud_database_url,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=3,
)