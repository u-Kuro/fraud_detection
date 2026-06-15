from services.fraud_api.src.modules.environment import environment
from sqlalchemy import create_engine, Engine

engine: Engine = create_engine(
    environment.postgres_fraud_database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)