from sqlalchemy import create_engine, Engine

engine: Engine = create_engine(
    "postgresql+psycopg2://",
    pool_pre_ping=True
)