from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import hash_password
from app.db.models.user import User
from app.schemas.user import UserCreate

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data: UserCreate):
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),)
        
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user