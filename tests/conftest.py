import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.db.base import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/user_management_test"
)
@pytest_asyncio.fixture(scope="function")
async def db():
    engine = create_async_engine(TEST_DATABASE_URL, isolation_level="AUTOCOMMIT")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
@pytest_asyncio.fixture(scope="function")
async def client(db):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    # Thisremembers which tokens were blacklisted during the test
    blacklisted_tokens = set()

    async def mock_blacklist(token, expires_in):
        blacklisted_tokens.add(token)

    async def mock_is_blacklisted(token):
        return token in blacklisted_tokens

    with patch("app.api.auth.blacklist_token", side_effect=mock_blacklist):
        with patch("app.api.auth.is_token_blacklisted", side_effect=mock_is_blacklisted):
            with patch("app.api.auth.publish_password_reset", new_callable=AsyncMock):
                async with AsyncClient(
                    transport=ASGITransport(app=app), base_url="http://test"
                ) as ac:
                    yield ac

    app.dependency_overrides.clear()