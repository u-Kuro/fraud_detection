from fastapi import Depends

from services.fraud_detection.src.main import app
from services.fraud_detection.src.modules.schemas.status import StatusResponse
from services.fraud_detection.src.services.dependencies import get_model, check_postgres, get_executor

@app.get(path="/health", include_in_schema=False)
async def health(): return StatusResponse(status="ok")

@app.get(
    path="/ready",
    include_in_schema=False,
    dependencies=[
        Depends(get_executor),
        Depends(get_model),
        Depends(check_postgres),
    ]
)
def ready(): return StatusResponse(status="ok")
