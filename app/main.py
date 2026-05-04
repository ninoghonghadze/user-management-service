from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.groups import router as groups_router
from app.api.users import router as users_router
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("User Management Service starting up...")
    yield
    logger.info("User Management Service shutting down...")


app = FastAPI(title="User Management Service", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "User Management Service is running"}


@app.get("/healthcheck")
async def healthcheck():
    logger.info("Health check called")
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(groups_router)
