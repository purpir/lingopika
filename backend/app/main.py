import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.session import async_engine
from app.db.base import Base
from app.api import auth, courses, lessons, hearts, xp, cards, leagues, premium, profile, users, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create tables (dev)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(hearts.router)
app.include_router(xp.router)
app.include_router(cards.router)
app.include_router(leagues.router)
app.include_router(premium.router)
app.include_router(profile.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
