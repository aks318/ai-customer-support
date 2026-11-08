from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.router import router
from app.core.config import settings
from app.db.mongodb import MongoDB

@asynccontextmanager
async def lifespan(app: FastAPI):
    # App start
    await MongoDB.connect()

    yield

    # App Stop
    await MongoDB.close()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI Powered Customer Support BE",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message" : "Welcome to AI Customer Support API"}