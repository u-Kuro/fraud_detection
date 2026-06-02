from services.drift_monitor.src.modules.environment import environment
from sqlalchemy import create_engine, Engine
from sqlalchemy.pool import NullPool

from services.drift_monitor.src.services.observability import observability

engine: Engine = create_engine(
    environment.postgres_fraud_database_url,
    poolclass=NullPool
)
observability.observe_sqlalchemy_engine(engine)