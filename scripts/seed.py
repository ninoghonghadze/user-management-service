import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.models.user import User, UserRole
from app.core.security import hash_password

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/user_management"

engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def seed():
    async with SessionLocal() as db:
        admin = User(
            name="Admin",
            surname="User",
            username="admin",
            email="admin@test.com",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
        )
        moderator = User(
            name="Moderator",
            surname="User",
            username="moderator",
            email="moderator@test.com",
            password_hash=hash_password("mod123"),
            role=UserRole.MODERATOR,
        )
        regular = User(
            name="Regular",
            surname="User",
            username="regular",
            email="regular@test.com",
            password_hash=hash_password("user123"),
            role=UserRole.USER,
        )
        db.add_all([admin, moderator, regular])
        await db.commit()
        print("✓ Admin created: username=admin password=admin123")
        print("✓ Moderator created: username=moderator password=mod123")
        print("✓ Regular user created: username=regular password=user123")

asyncio.run(seed())