from services.drift_monitor.src.modules.environment import environment
from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import NullPool

engine: Engine = create_engine(
    environment.postgres_fraud_database_url,
    poolclass=NullPool
)