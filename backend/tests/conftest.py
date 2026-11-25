import os
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./lingopika.db")
os.environ.setdefault("SYNC_DATABASE_URL", "sqlite:///./lingopika.db")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DEBUG", "true")

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
