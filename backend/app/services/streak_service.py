from datetime import datetime, timezone, date, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import DailyStreak, User, UserSettings
from app.services.xp_service import award_xp


def user_today(user: User) -> str:
    tz_name = "UTC"
    if user.settings:
        tz_name = user.settings.timezone or "UTC"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = timezone.utc
    return datetime.now(tz).date().isoformat()


async def record_activity(db: AsyncSession, user: User) -> DailyStreak:
    result = await db.execute(select(DailyStreak).where(DailyStreak.user_id == user.id))
    streak = result.scalar_one_or_none()
    if not streak:
        streak = DailyStreak(user_id=user.id)
        db.add(streak)
        await db.flush()
    today = user_today(user)
    if streak.last_activity_date == today:
        return streak
    if streak.last_activity_date:
        try:
            last = date.fromisoformat(streak.last_activity_date)
            cur = date.fromisoformat(today)
            if (cur - last).days == 1:
                streak.current_streak += 1
            elif (cur - last).days > 1:
                streak.current_streak = 1
            else:
                # same or past; keep
                pass
        except ValueError:
            streak.current_streak = 1
    else:
        streak.current_streak = 1
    streak.last_activity_date = today
    streak.total_active_days += 1
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak
    await db.flush()
    # daily xp bonus
    await award_xp(db, user, 10, "daily_bonus", source_id=today, idempotency_key=f"daily_bonus:{user.id}:{today}")
    return streak
