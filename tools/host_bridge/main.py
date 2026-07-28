from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from tools.host_bridge.controllers.routers import act

@asynccontextmanager
async def lifespan(_):
    yield

app = FastAPI(
    title="host-bridge",
    lifespan=lifespan
)

# Routers
app.include_router(act.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9080)