from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (create_access_token, create_refresh_token,
                               decode_access_token, verify_password)
from app.db.session import get_db
from app.schemas.auth import (LoginRequest, PasswordResetRequest,
                              RefreshRequest, TokenResponse)
from app.schemas.user import UserCreate, UserResponse
from app.services.rabbitmq_service import publish_password_reset
from app.services.redis_service import blacklist_token, is_token_blacklisted
from app.services.user_service import (create_user, get_user_by_email,
                                       get_user_by_phone, get_user_by_username)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if await get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        user = await create_user(db, user_data)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # try username, then email, then phone number
    user = await get_user_by_username(db, data.username)
    if not user:
        user = await get_user_by_email(db, data.username)
    if not user:
        user = await get_user_by_phone(db, data.username)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="User is blocked")
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest):
    if await is_token_blacklisted(data.refresh_token):
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")

    try:
        payload = decode_access_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
        exp = payload.get("exp")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    expires_in = exp - int(datetime.now(timezone.utc).timestamp())
    await blacklist_token(data.refresh_token, max(expires_in, 1))

    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)
    return TokenResponse(access_token=new_access_token, refresh_token=new_refresh_token)


@router.post("/reset-password", status_code=status.HTTP_202_ACCEPTED)
async def reset_password(
    data: PasswordResetRequest, db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_email(db, data.email)

    if user:
        reset_link = f"https://yourapp.com/reset?token=dummy_token_for_{user.id}"
        await publish_password_reset(data.email, reset_link)

    return {"message": "If this email exists, a reset link has been sent"}
