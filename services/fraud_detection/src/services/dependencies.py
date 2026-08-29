from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException
from sqlalchemy import select
from starlette.requests import Request

from services.fraud_detection.src.repositories.postgres.postgres import sql_session
from services.fraud_detection.src.services.fraud_classifier import FraudClassifier

async def get_executor(request: Request) -> ThreadPoolExecutor:
    executor = request.app.state.executor
    if executor is None:
        raise HTTPException(status_code=503, detail="Executor is not ready.")
    else:
        return executor

async def get_model(request: Request) -> FraudClassifier:
    model = request.app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not ready.")
    else:
        return model

def check_postgres():
    try:
        with sql_session.begin() as session:
            session.execute(select(1))
    except:
        raise HTTPException(status_code=503, detail=f"Database is not ready.")