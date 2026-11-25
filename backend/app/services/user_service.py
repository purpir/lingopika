from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User, UserProfile, UserSettings, Hearts, DailyStreak
from app.config import settings


from sqlalchemy.orm import selectinload

async def get_or_create_user(db: AsyncSession, tg_user: dict) -> User:
    telegram_id = int(tg_user["id"])
    result = await db.execute(select(User).options(selectinload(User.profile), selectinload(User.settings), selectinload(User.hearts), selectinload(User.streak)).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user:
        user.username = tg_user.get("username")
        user.first_name = tg_user.get("first_name")
        user.last_name = tg_user.get("last_name")
        user.language_code = tg_user.get("language_code")
        user.photo_url = tg_user.get("photo_url")
        user.last_active_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        if telegram_id in settings.admin_ids:
            user.is_admin = True
        return user

    user = User(
        telegram_id=telegram_id,
        username=tg_user.get("username"),
        first_name=tg_user.get("first_name"),
        last_name=tg_user.get("last_name"),
        language_code=tg_user.get("language_code"),
        photo_url=tg_user.get("photo_url"),
        is_admin=telegram_id in settings.admin_ids,
        last_active_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )
    db.add(user)
    await db.flush()

    profile = UserProfile(user_id=user.id, english_level="beginner")
    settings_row = UserSettings(user_id=user.id, timezone="UTC")
    hearts = Hearts(user_id=user.id, count=settings.HEART_MAX, max_count=settings.HEART_MAX)
    streak = DailyStreak(user_id=user.id)
    db.add_all([profile, settings_row, hearts, streak])
    await db.flush()
    user.profile = profile
    user.settings = settings_row
    user.hearts = hearts
    user.streak = streak
    return user


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> User | None:
    result = await db.execute(select(User).options(selectinload(User.profile), selectinload(User.settings), selectinload(User.hearts), selectinload(User.streak)).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def set_onboarding(db: AsyncSession, user: User, english_level: str) -> UserProfile:
    profile = user.profile
    profile.english_level = english_level
    profile.onboarding_completed = True
    # set current lesson to first of appropriate level
    from app.db.models import Lesson
    res = await db.execute(select(Lesson).where(Lesson.level == level_to_course_level(english_level)).order_by(Lesson.number).limit(1))
    first = res.scalar_one_or_none()
    if first:
        profile.current_lesson_id = first.id
    await db.flush()
    return profile


def level_to_course_level(level: str) -> str:
    mapping = {
        "nothing": "A1",
        "beginner": "A1",
        "a1": "A1",
        "a2": "A2",
        "b1": "B1",
        "b2": "B2",
        "c1": "C1",
    }
    return mapping.get(level.lower(), "A1")
