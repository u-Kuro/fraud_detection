from pydantic import BaseModel, StrictStr

class StatusResponse(BaseModel):
    status: StrictStr