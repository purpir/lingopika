from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Hearts, User
from app.config import settings


def _now():
    return datetime.now(timezone.utc)


def _aware(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def get_hearts(db: AsyncSession, user: User) -> Hearts:
    result = await db.execute(select(Hearts).where(Hearts.user_id == user.id))
    hearts = result.scalar_one_or_none()
    if not hearts:
        hearts = Hearts(user_id=user.id, count=settings.HEART_MAX, max_count=settings.HEART_MAX)
        db.add(hearts)
        await db.flush()
    # regen
    await regen_hearts(db, hearts)
    return hearts


async def regen_hearts(db: AsyncSession, hearts: Hearts) -> Hearts:
    if hearts.count >= hearts.max_count:
        hearts.next_regen_at = None
        return hearts
    now = _now()
    # ensure last_regen_at
    if hearts.last_regen_at is None:
        hearts.last_regen_at = now
        hearts.next_regen_at = now + timedelta(hours=settings.HEART_REGEN_HOURS)
        return hearts
    # process regen intervals
    regen_hours = timedelta(hours=settings.HEART_REGEN_HOURS)
    if hearts.next_regen_at is None:
        hearts.next_regen_at = _aware(hearts.last_regen_at) + regen_hours
    else:
        hearts.next_regen_at = _aware(hearts.next_regen_at)
    while hearts.count < hearts.max_count and hearts.next_regen_at is not None and now >= hearts.next_regen_at:
        hearts.count += 1
        hearts.last_regen_at = hearts.next_regen_at
        if hearts.count < hearts.max_count:
            hearts.next_regen_at = hearts.last_regen_at + regen_hours
        else:
            hearts.next_regen_at = None
    if hearts.count < hearts.max_count and hearts.next_regen_at is None:
        hearts.next_regen_at = (hearts.last_regen_at or now) + regen_hours
    hearts.last_regen_at = _aware(hearts.last_regen_at) if hearts.last_regen_at else now
    return hearts


async def spend_heart(db: AsyncSession, user: User, amount: int = 1) -> Hearts:
    hearts = await get_hearts(db, user)
    # premium: infinite
    profile = user.profile
    if profile.is_premium:
        return hearts
    if hearts.count < amount:
        raise ValueError("Not enough hearts")
    hearts.count = max(0, hearts.count - amount)
    now = _now()
    if hearts.count < hearts.max_count and hearts.next_regen_at is None:
        hearts.last_regen_at = now
        hearts.next_regen_at = now + timedelta(hours=settings.HEART_REGEN_HOURS)
    await db.flush()
    return hearts


async def refill_hearts(db: AsyncSession, user: User, amount: int) -> Hearts:
    hearts = await get_hearts(db, user)
    hearts.count = min(hearts.max_count, hearts.count + amount)
    if hearts.count >= hearts.max_count:
        hearts.next_regen_at = None
    await db.flush()
    return hearts


async def set_infinite(db: AsyncSession, user: User, enabled: bool) -> None:
    hearts = await get_hearts(db, user)
    if enabled:
        hearts.count = hearts.max_count
        hearts.next_regen_at = None
    await db.flush()
