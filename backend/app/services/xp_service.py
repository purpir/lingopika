from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import XPTransaction, User, UserProfile

XP_PER_LEVEL = 100


async def award_xp(db: AsyncSession, user: User, amount: int, reason: str, source_id: str | None = None, idempotency_key: str | None = None) -> int:
    if amount <= 0:
        return 0
    if idempotency_key:
        existing = await db.execute(select(XPTransaction).where(XPTransaction.idempotency_key == idempotency_key))
        if existing.scalar_one_or_none():
            return 0
    tx = XPTransaction(user_id=user.id, amount=amount, reason=reason, source_id=source_id, idempotency_key=idempotency_key)
    db.add(tx)
    profile = user.profile
    profile.total_xp += amount
    profile.level = max(1, profile.total_xp // XP_PER_LEVEL + 1)
    await db.flush()
    return amount


def xp_to_next_level(profile: UserProfile) -> int:
    current_level_xp = (profile.level - 1) * XP_PER_LEVEL
    next_level_xp = profile.level * XP_PER_LEVEL
    return max(0, next_level_xp - profile.total_xp)
