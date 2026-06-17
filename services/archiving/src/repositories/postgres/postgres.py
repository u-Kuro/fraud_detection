from services.archiving.src.modules.environment import environment
from sqlalchemy import create_engine, Engine

engine: Engine = create_engine(
    environment.POSTGRES_FRAUD_DB_URL,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=3,
)