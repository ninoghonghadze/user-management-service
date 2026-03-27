from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.users import router as users_router

app = FastAPI(title="User Management Service")

@app.get("/")
async def root():
    return {"message": "User Management Service is running"}

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(users_router)