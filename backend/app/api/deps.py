from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.utils.jwt import decode_access_token
from app.db.models import User
from app.config import settings


async def get_current_user(
    authorization: str | None = Header(default=None),
    x_telegram_init_data: str | None = Header(default=None, alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db),
) -> User:
    telegram_id = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
        sub = decode_access_token(token)
        if sub:
            try:
                telegram_id = int(sub)
            except ValueError:
                telegram_id = None
    if telegram_id is None and x_telegram_init_data:
        from app.utils.telegram_auth import extract_telegram_user
        tg_user = extract_telegram_user(x_telegram_init_data)
        if tg_user:
            telegram_id = int(tg_user["id"])
    if telegram_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    result = await db.execute(select(User).options(selectinload(User.profile), selectinload(User.settings), selectinload(User.hearts), selectinload(User.streak)).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return user
